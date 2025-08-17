from ... import _hub

# TODO model refactoring: use matrices as building blocks,
# it will save some effort (Cell, CellLayer etc.)

# decompress ; b64decode ; struct... Sont tous 3
# employés dans Layer.fromxml
# TODO check if its katasdk -compatible?
from zlib import decompress
from base64 import b64decode
import struct

# ElemenTree est employé en 2 endroits: dans Tileset.fromxml & Tilemap.load
# this works in local ctx:
# from xml.etree import ElementTree
from xml.etree import ElementTree


def load_tmx(filename):
    return TileMap.load(filename)


class Cell:
    """
    Layers are made of Cells (or empty space).
    Cells have some basic properties:

    x, y - the cell's index in the layer
    px, py - the cell's pixel position
    left, right, top, bottom - the cell's pixel boundaries

    Additionally the cell may have other properties which are accessed using
    standard dictionary methods:

    cell['property name']

    You may assign a new value for a property to or even delete an existing
    property from the cell - this will not affect the Tile or any other Cells
    using the Cell's Tile.
    """

    def __init__(self, x, y, px, py, tile):
        self.x, self.y = x, y
        self.px, self.py = px, py
        self.tile = tile
        self.topleft = (px, py)
        self.left = px
        self.right = px + tile.tile_width
        self.top = py
        self.bottom = py + tile.tile_height
        self.center = (px + tile.tile_width // 2, py + tile.tile_height // 2)
        self._added_properties = {}
        self._deleted_properties = set()

    def __repr__(self):
        return '<Cell %s,%s %d>' % (self.px, self.py, self.tile.gid)

    def __contains__(self, key):
        if key in self._deleted_properties:
            return False
        return key in self._added_properties or key in self.tile.properties

    def __getitem__(self, key):
        if key in self._deleted_properties:
            raise KeyError(key)
        if key in self._added_properties:
            return self._added_properties[key]
        if key in self.tile.properties:
            return self.tile.properties[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        self._added_properties[key] = value

    def __delitem__(self, key):
        self._deleted_properties.add(key)

    def intersects(self, other):
        """
        Determine whether this Cell intersects with the other rect (which has
        .x, .y, .width and .height attributes.)
        """
        if self.px + self.tile.tile_width < other.x:
            return False
        if other.x + other.width - 1 < self.px:
            return False
        if self.py + self.tile.tile_height < other.y:
            return False
        if other.y + other.height - 1 < self.py:
            return False
        return True


class LayerIterator(object):
    """
    Iterates over all the cells in a layer in column,row order.
    """

    def __init__(self, layer):
        self.layer = layer
        self.i, self.j = 0, 0

    def __next__(self):
        if self.i == self.layer.width - 1:
            self.j += 1
            self.i = 0
        if self.j == self.layer.height - 1:
            raise StopIteration()
        value = self.layer[self.i, self.j]
        self.i += 1
        return value


# TODO faut sortir draw
class ObjectTmx:
    """An object in a TMX object layer.
    name: The name of the object. An arbitrary string.
    type: The type of the object. An arbitrary string.
    x: The x coordinate of the object in pixels.
    y: The y coordinate of the object in pixels.
    width: The width of the object in pixels (defaults to 0).
    height: The height of the object in pixels (defaults to 0).
    gid: An reference to a tile (optional).
    visible: Whether the object is shown (1) or hidden (0). Defaults to 1.
    """

    def __init__(self, type, x, y, width=0, height=0, name=None,
                 gid=None, tile=None, visible=1):
        self.type = type
        self.px = x
        self.left = x
        if tile:
            y -= tile.tile_height
            width = tile.tile_width
            height = tile.tile_height
        self.py = y
        self.top = y
        self.width = width
        self.right = x + width
        self.height = height
        self.bottom = y + height
        self.name = name
        self.gid = gid
        self.tile = tile
        self.visible = visible
        self.properties = {}

        self._added_properties = {}
        self._deleted_properties = set()
        self.pyg = _hub.pygame

    def __repr__(self):
        if self.tile:
            return '<Object %s,%s %s,%s tile=%d>' % (self.px, self.py, self.width, self.height, self.gid)
        else:
            return '<Object %s,%s %s,%s>' % (self.px, self.py, self.width, self.height)

    def __contains__(self, key):
        if key in self._deleted_properties:
            return False
        if key in self._added_properties:
            return True
        if key in self.properties:
            return True
        return self.tile and key in self.tile.properties

    def __getitem__(self, key):
        if key in self._deleted_properties:
            raise KeyError(key)
        if key in self._added_properties:
            return self._added_properties[key]
        if key in self.properties:
            return self.properties[key]
        if self.tile and key in self.tile.properties:
            return self.tile.properties[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        self._added_properties[key] = value

    def __delitem__(self, key):
        self._deleted_properties.add(key)

    def draw(self, surface, view_x, view_y):
        if self.visible:
            x, y = (self.px - view_x, self.py - view_y)
            if self.tile:
                surface.blit(self.tile.surface, (x, y))
            else:
                r = self.pyg.Rect((x, y), (self.width, self.height))
                self.pyg.draw.rect(surface, (255, 100, 100), r, 2)

    @classmethod
    def fromxml(cls, tag, map):
        if 'gid' in tag.attrib:
            gid = int(tag.attrib['gid'])
            tile = map.tilesets[gid]
            w = tile.tile_width
            h = tile.tile_height
        else:
            gid = None
            tile = None
            w = round(float(tag.attrib['width']))
            h = round(float(tag.attrib['height']))

        x_attr, y_attr = round(float(tag.attrib['x'])), round(float(tag.attrib['y']))
        o = cls(
            tag.attrib.get('type', 'rect'),
            x_attr, y_attr, w, h, tag.attrib.get('name'), gid, tile,
            int(tag.attrib.get('visible', 1))
        )

        props = tag.find('properties')
        if props is None:
            return o

        for c in props.findall('property'):
            # store additional properties.
            name = c.attrib['name']
            value = c.attrib['value']

            # TODO hax
            if value.isdigit():
                value = int(value)
            o.properties[name] = value
        return o

    def intersects(self, x1, y1, x2, y2):
        return not any((x2 < self.px, y2 < self.py, x1 > self.px + self.width, y1 > self.py + self.height))


# TODO la aussi, deux methodes de dessin a evacuer!
class ObjectLayer:
    """
    A layer composed of basic primitive shapes.
    Actually encompasses a TMX <objectgroup> but even the TMX documentation
    refers to them as object layers, so I will.

    ObjectLayers have some basic properties:

        position - ignored (cannot be edited in the current Tiled editor)
        name - the name of the object group.
        color - the color used to display the objects in this group.
        opacity - the opacity of the layer as a value from 0 to 1.
        visible - whether the layer is shown (1) or hidden (0).
        objects - the objects in this Layer (Object instances)
    """

    def __init__(self, name, color, objects, opacity=1,
                 visible=1, position=(0, 0)):
        self.name = name
        self.color = color
        self.objects = objects
        self.opacity = opacity
        self.visible = visible
        self.position = position
        self.properties = {}

    def __repr__(self):
        return '<ObjectLayer "%s" at 0x%x>' % (self.name, id(self))

    @classmethod
    def fromxml(cls, tag, map):
        layer = cls(tag.attrib['name'], tag.attrib.get('color'), [],
                    float(tag.attrib.get('opacity', 1)),
                    int(tag.attrib.get('visible', 1)))
        for object in tag.findall('object'):
            layer.objects.append(ObjectTmx.fromxml(object, map))
        for c in tag.findall('property'):
            # store additional properties.
            name = c.attrib['name']
            value = c.attrib['value']

            # TODO hax
            if value.isdigit():
                value = int(value)
            layer.properties[name] = value
        return layer

    def update(self, dt, *args):
        pass

    def set_view(self, x, y, w, h, viewport_ox=0, viewport_oy=0):
        self.view_x, self.view_y = x, y
        self.view_w, self.view_h = w, h
        x -= viewport_ox
        y -= viewport_oy
        self.position = (x, y)

    def draw(self, surface):
        """
        Draw this layer, limited to the current viewport, to the Surface.
        """
        if not self.visible:
            return
        ox, oy = self.position
        w, h = self.view_w, self.view_h
        for myobj in self.objects:
            myobj.draw(surface, self.view_x, self.view_y)

    def find(self, *properties):
        """
        Find all cells with the given properties set.
        """
        r = []
        for propname in properties:
            for myobj in self.objects:
                if myobj and propname in myobj or propname in self.properties:
                    r.append(myobj)
        return r

    def match(self, **properties):
        """
        Find all objects with the given properties set to the given values.
        """
        r = []
        for propname in properties:
            for myobj in self.objects:
                if propname in myobj:
                    val = myobj[propname]
                elif propname in self.properties:
                    val = self.properties[propname]
                else:
                    continue
                if properties[propname] == val:
                    r.append(myobj)
        return r

    def collide(self, rect, propname):
        """
        Find all objects the rect is touching that have the indicated
        property name set.
        """
        r = []
        for myobj in self.get_in_region(rect.left, rect.top, rect.right, rect.bottom):
            if propname in myobj or propname in self.properties:
                r.append(myobj)
        return r

    def get_in_region(self, x1, y1, x2, y2):
        """
        Return objects that are within the map-space
        pixel bounds specified by the bottom-left (x1, y1) and top-right
        (x2, y2) corners.

        Return a list of Object instances.
        """
        return [obj for obj in self.objects if obj.intersects(x1, y1, x2, y2)]

    def get_at(self, x, y):
        """
        Return the first object found at the nominated (x, y) coordinate.
        Return an Object instance or None.
        """
        for myobj in self.objects:
            if myobj.contains(x, y):
                return myobj


# TODO y a deux methodes a evacuer c'est set_view(...) et draw(...)
class Layer:
    """
    A 2d grid of Cells.

    Layers have some basic properties:

        width, height - the dimensions of the Layer in cells
        tile_width, tile_height - the dimensions of each cell
        px_width, px_height - the dimensions of the Layer in pixels
        tilesets - the tilesets used in this Layer (a Tilesets instance)
        properties - any properties set for this Layer
        cells - a dict of all the Cell instances for this Layer, keyed off
                (x, y) index.

    Additionally you may look up a cell using direct item access:

       layer[x, y] is layer.cells[x, y]

    Note that empty cells will be set to None instead of a Cell instance.
    """

    def __init__(self, name, visible, map):
        self.name = name
        self.visible = visible
        self.position = (0, 0)
        # TODO get from TMX?
        self.px_width = map.px_width
        self.px_height = map.px_height
        self.tile_width = map.tile_width
        self.tile_height = map.tile_height
        self.width = map.width
        self.height = map.height
        self.tilesets = map.tilesets
        self.group = _hub.pygame.sprite.Group()
        self.properties = {}
        self.cells = {}

    def __repr__(self):
        return '<Layer "%s" at 0x%x>' % (self.name, id(self))

    def __getitem__(self, pos):
        return self.cells.get(pos)

    def __setitem__(self, pos, tile):
        x, y = pos
        px = x * self.tile_width
        py = y * self.tile_width
        self.cells[pos] = Cell(x, y, px, py, tile)

    def __iter__(self):
        return LayerIterator(self)

    @classmethod
    def fromxml(cls, tag, givenmap):
        layer = cls(tag.attrib['name'], int(tag.attrib.get('visible', 1)), givenmap)

        data = tag.find('data')
        if data is None:
            raise ValueError('layer %s does not contain <data>' % layer.name)

        data = data.text.strip()
        data = data.encode()  # Convert to bytes
        # Decode from base 64 and decompress via zlib
        data = decompress(b64decode(data))
        data = struct.unpack('<%di' % (len(data) / 4,), data)
        assert len(data) == layer.width * layer.height
        for idx, gid in enumerate(data):
            if gid >= 1:  # otherwise its not set
                tile = givenmap.tilesets[gid]
                x = idx % layer.width
                y = idx // layer.width
                layer.cells[x, y] = Cell(x, y, x * givenmap.tile_width, y * givenmap.tile_height, tile)

        return layer

    def update(self, dt, *args):
        pass

    def set_view(self, x, y, w, h, viewport_ox=0, viewport_oy=0):
        self.view_x, self.view_y = x, y
        self.view_w, self.view_h = w, h
        x -= viewport_ox
        y -= viewport_oy
        self.position = (x, y)

    def draw(self, surface):
        """
        Draw this layer, limited to the current viewport, to the Surface.
        """
        ox, oy = self.position
        w, h = self.view_w, self.view_h
        for x in range(ox, ox + w + self.tile_width, self.tile_width):
            i = x // self.tile_width
            for y in range(oy, oy + h + self.tile_height, self.tile_height):
                j = y // self.tile_height
                if (i, j) not in self.cells:
                    continue
                cell = self.cells[i, j]
                surface.blit(cell.tile.surface, (cell.px - ox, cell.py - oy))

    def find(self, *properties):
        """
        Find all cells with the given properties set.
        """
        r = []
        for propname in properties:
            for cell in list(self.cells.values()):
                if cell and propname in cell:
                    r.append(cell)
        return r

    def match(self, **properties):
        """
        Find all cells with the given properties set to the given values.
        """
        r = []
        for propname in properties:
            for cell in list(self.cells.values()):
                if propname not in cell:
                    continue
                if properties[propname] == cell[propname]:
                    r.append(cell)
        return r

    def collide(self, rect, propname):
        """
        Find all cells the rect is touching that have the indicated property
        name set.
        """
        r = []
        for cell in self.get_in_region(rect.left, rect.top, rect.right,
                                       rect.bottom):
            if not cell.intersects(rect):
                continue
            if propname in cell:
                r.append(cell)
        return r

    def get_in_region(self, x1, y1, x2, y2):
        """
        Return cells (in [column][row]) that are within the map-space
        pixel bounds specified by the bottom-left (x1, y1) and top-right
        (x2, y2) corners.
        Return a list of Cell instances.
        """
        i1 = max(0, x1 // self.tile_width)
        j1 = max(0, y1 // self.tile_height)
        i2 = min(self.width, x2 // self.tile_width + 1)
        j2 = min(self.height, y2 // self.tile_height + 1)
        return [self.cells[i, j]
                for i in range(int(i1), int(i2))
                for j in range(int(j1), int(j2))
                if (i, j) in self.cells]

    def get_at(self, x, y):
        """
        Return the cell at the nominated (x, y) coordinate.
        Return a Cell instance or None.
        """
        i = x // self.tile_width
        j = y // self.tile_height
        return self.cells.get((i, j))

    def neighbors(self, index):
        """
        Return the indexes of the valid (ie. within the map) cardinal (ie.
        North, South, East, West) neighbors of the nominated cell index.
        Returns a list of 2-tuple indexes.
        """
        i, j = index
        n = []
        if i < self.width - 1:
            n.append((i + 1, j))
        if i > 0:
            n.append((i - 1, j))
        if j < self.height - 1:
            n.append((i, j + 1))
        if j > 0:
            n.append((i, j - 1))
        return n


class Tile:

    def __init__(self, gid, surface, tileset):
        self.gid = gid
        self.surface = surface
        self.tile_width = tileset.tile_width
        self.tile_height = tileset.tile_height
        self.properties = {}

    @classmethod
    def fromSurface(cls, surface):
        """
        Create a new Tile object straight from a pygame Surface.
        Its tile_width and tile_height will be set using the Surface dimensions.
        Its gid will be 0.
        """
        class ts:
            tile_width, tile_height = surface.get_size()

        return cls(0, surface, ts)

    def loadxml(self, tag):
        props = tag.find('properties')
        if props is None:
            return
        for c in props.findall('property'):
            # store additional properties.
            name = c.attrib['name']
            value = c.attrib['value']

            # TODO hax
            if value.isdigit():
                value = int(value)
            self.properties[name] = value

    def __repr__(self):
        return '<Tile %d>' % self.gid


class Tileset:
    """
    (mm si l'on charge des img pygame ca reste du modele car on fetch les donnees depuis
    une telle instance...)
    """

    def __init__(self, name, tile_width, tile_height, firstgid):
        self.name = name
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.firstgid = firstgid
        self.tiles = []
        self.properties = {}

    def add_image(self, file):
        image = _hub.pygame.image.load(file).convert_alpha()
        if not image:
            print("Error creating new Tileset: file %s not found" % file)
            raise FileNotFoundError

        ident = self.firstgid
        tile_w, tile_h = self.tile_width, self.tile_height
        for line in range(image.get_height() // tile_h):
            for column in range(image.get_width() // tile_w):
                pos = _hub.pygame.Rect(column * tile_w, line * tile_h, tile_w, tile_h)
                self.tiles.append(Tile(ident, image.subsurface(pos), self))
                ident += 1

    def get_tile(self, gid):
        return self.tiles[gid - self.firstgid]

    @classmethod
    def fromxml(cls, tag, firstgid=None, hacksource=None, hacktileset=None):
        print('fromxml ')
        if 'source' in tag.attrib:
            firstgid = int(tag.attrib['firstgid'])
            if hacksource:
                srcc = hacksource
            else:
                srcc = tag.attrib['source']

            with open(srcc) as f:
                print('opened ', srcc)
                tileset = ElementTree.fromstring(f.read())

            return cls.fromxml(tileset, firstgid, hacktileset=hacktileset)

        name = tag.attrib['name']
        if firstgid is None:
            firstgid = int(tag.attrib['firstgid'])
        tile_width = int(tag.attrib['tilewidth'])
        tile_height = int(tag.attrib['tileheight'])

        tileset = cls(name, tile_width, tile_height, firstgid)

        for c in tag:  # .getchildren():
            if c.tag == "image":
                # create a tileset
                arg_sheet = c.attrib['source'] if (hacktileset is None) else hacktileset
                tileset.add_image(arg_sheet)
            elif c.tag == 'tile':
                gid = tileset.firstgid + int(c.attrib['id'])
                tileset.get_tile(gid).loadxml(c)
        return tileset


class Tilesets(dict):
    def add(self, tileset):
        for idx, tile in enumerate(tileset.tiles):
            idx += tileset.firstgid
            self[idx] = tile


class Layers(list):
    def __init__(self):
        self.by_name = {}

    def add_named(self, layer, name):
        self.append(layer)
        self.by_name[name] = layer

    def __getitem__(self, item):
        if isinstance(item, int):
            return self[item]
        return self.by_name[item]


class TileMap:
    """
    A TileMap is a collection of Layers which contain gridded maps or sprites
    TileMaps are loaded from TMX files which sets the .layers and .tilesets properties

    After loading, additional SpriteLayers may be added.

    A TileMap's rendering is restricted by a viewport which is defined by the
    size passed in at construction time and the focus set by set_focus() or
    force_focus().

    TileMaps have a number of properties:

        width, height - the dimensions of the tilemap in cells

        tile_width, tile_height - the dimensions of the cells in the map
        px_width, px_height - the dimensions of the tilemap in pixels
        properties - any properties set on the tilemap in the TMX file
        layers - all layers of this tilemap as a Layers instance
        tilesets - all tilesets of this tilemap as a Tilesets instance

    """

    def __init__(self):
        self.px_width = 0
        self.px_height = 0
        self.tile_width = 0
        self.tile_height = 0
        self.width = 0
        self.height = 0
        self.properties = {}
        self.layers = Layers()
        self.tilesets = Tilesets()

    @property
    def pix_width(self):
        return self.px_width

    @property
    def pix_height(self):
        return self.px_height

    def update(self, dt, *args):
        for layer in self.layers:
            layer.update(dt, *args)

    @classmethod
    def load(cls, filename, hack_tsxfile=None, hack_ts=None):
        with open(filename) as f:
            tminfo_tree = ElementTree.fromstring(f.read())

        # get most general map informations and create a surface
        tilemap = TileMap()

        tilemap.width = int(tminfo_tree.attrib['width'])
        tilemap.height = int(tminfo_tree.attrib['height'])
        tilemap.tile_width = int(tminfo_tree.attrib['tilewidth'])
        tilemap.tile_height = int(tminfo_tree.attrib['tileheight'])
        tilemap.px_width = tilemap.width * tilemap.tile_width
        tilemap.px_height = tilemap.height * tilemap.tile_height

        for tag in tminfo_tree.findall('tileset'):
            tilemap.tilesets.add(
                Tileset.fromxml(tag, hacksource=hack_tsxfile, hacktileset=hack_ts)  # hacks work only if no more than 1 ts
            )
            print('tilesets added')

        for tag in tminfo_tree.findall('layer'):
            layer = Layer.fromxml(tag, tilemap)
            tilemap.layers.add_named(layer, layer.name)

        for tag in tminfo_tree.findall('objectgroup'):
            layer = ObjectLayer.fromxml(tag, tilemap)
            tilemap.layers.add_named(layer, layer.name)

        # We wanna persist info about the (optional) Image layer found in .tmx
        # TODO add to kengi a class that modelize ImageLayer?
        tagraw_ilayer_li = tminfo_tree.findall('imagelayer')
        if len(tagraw_ilayer_li) == 1:
            tagraw_ilayer = tagraw_ilayer_li.pop()
            subnode = tagraw_ilayer.find('image')
            tilemap.background = {  # persist info in tilemap_obj.background
                'img_path': subnode.attrib['source'],
                'offsetx': round(float(tagraw_ilayer.attrib['offsetx'])),
                'offsety': round(float(tagraw_ilayer.attrib['offsety'])),
                'repeatx': int(tagraw_ilayer.attrib['repeatx'])  # 0 or 1
            }
        elif len(tagraw_ilayer_li) > 1:
            raise NotImplementedError
        else:
            tilemap.background = None

        return tilemap
