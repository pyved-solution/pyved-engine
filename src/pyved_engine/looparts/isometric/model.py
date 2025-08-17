import json
import math
import os
import struct
from base64 import b64decode
from xml.etree import ElementTree
from zlib import decompress
from ... import pe_vars
from .flags import *
from ... import _hub


info_type_obj = 'class'


class IsometricTile:
    def __init__(self, tile_id, tile_surface):
        self.id = tile_id

        self.tile_surface = tile_surface
        self.anchor = list(tile_surface.get_size())
        self.anchor[0] = self.anchor[0]//2  # int(0.5*self.anchor[0])

        self.images = {
            (False, False): tile_surface,
            (True, False): _hub.pygame.transform.flip(tile_surface, True, False),
            (False, True): _hub.pygame.transform.flip(tile_surface, False, True),
            (True, True): _hub.pygame.transform.flip(tile_surface, True, True),
        }

        self.hflip_surface = None
        self.vflip_surface = None
        self.hvflip_surface = None

    def paint_tile(self, dest_surface, x, y, hflip=False, vflip=False):
        """Draw this tile on the dest_surface at the provided x,y coordinates."""

        if (not hflip) and (not vflip):
            dest_surface.blit(self.tile_surface, (x-self.anchor[0], y-self.anchor[1]))
            return

        if hflip and vflip:
            if self.hvflip_surface is None:
                self.hvflip_surface = _hub.pygame.transform.flip(self.tile_surface, True, True)
                self.hvflip_surface.set_colorkey(self.tile_surface.get_colorkey(), self.tile_surface.get_flags())
            surf = self.hvflip_surface

        elif hflip:
            if self.hflip_surface is None:
                self.hflip_surface = _hub.pygame.transform.flip(self.tile_surface, True, False)
                self.hflip_surface.set_colorkey(self.tile_surface.get_colorkey(), self.tile_surface.get_flags())
            surf = self.hflip_surface

        elif vflip:
            if self.vflip_surface is None:
                self.vflip_surface = _hub.pygame.transform.flip(self.tile_surface, False, True)
                self.vflip_surface.set_colorkey(self.tile_surface.get_colorkey(), self.tile_surface.get_flags())
            surf = self.vflip_surface

        mydest = surf.get_rect(midbottom=(x, y))
        dest_surface.blit(surf, mydest)

    def __repr__(self):
        return '<Tile {}>'.format(self.id)


class IsometricTileset:
    """
    Based on the Tileset class from katagames_engine/_sm_shelf/tmx/data.py, but modified for the needs of isometric
    maps. Or at least the needs of this particular isometric map.
    """

    def __init__(self, name, tile_width, tile_height, firstgid):
        self.name = name
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.firstgid = firstgid

        # self.hflip = False
        # self.vflip = False

        self.tiles = []
        self.properties = {}

    def get_tile(self, gid):
        return self.tiles[gid - self.firstgid]

    def _add_image(self, folders, source, num_tiles):
        # TODO: Make this bit compatible with Kenji.
        # mysurf = _hub.pygame.image.load(os.path.join(os.sep.join(folders), source)).convert_alpha()
        mysurf = vars.images[source.split('.')[0]]
        mysurf.set_colorkey((255, 0, 255))
        myrect = _hub.pygame.Rect(0, 0, self.tile_width, self.tile_height)
        frames_per_row = mysurf.get_width() // self.tile_width

        for frame in range(num_tiles):
            myrect.x = (frame % frames_per_row) * self.tile_width
            myrect.y = (frame // frames_per_row) * self.tile_height
            self.tiles.append(IsometricTile(frame + 1, mysurf.subsurface(myrect)))

    @classmethod
    def fromxml(cls, folders, tag, firstgid=None):
        print('[isometric.model] method .fromxml has been called')
        if 'source' in tag.attrib:
            # Instead of a tileset proper, we have been handed an external tileset tag from inside a map file.
            # Load the external tileset and continue on as if nothing had happened.
            firstgid = int(tag.attrib['firstgid'])
            srcc = tag.attrib['source']

            # TODO: Another direct disk access here.
            if srcc.endswith(("tsx", "xml")):
                with open(os.path.join(*folders, srcc)) as f:
                    tag = ElementTree.fromstring(f.read())
            elif srcc.endswith(("tsj", "json")):
                with open(os.path.join(*folders, srcc)) as f:
                    jdict = json.load(f)
                return cls.fromjson(folders, jdict, firstgid)

        name = tag.attrib['name']
        if firstgid is None:
            firstgid = int(tag.attrib['firstgid'])
        tile_width = int(tag.attrib['tilewidth'])
        tile_height = int(tag.attrib['tileheight'])
        num_tiles = int(tag.attrib['tilecount'])

        tileset = cls(name, tile_width, tile_height, firstgid)

        # TODO: The transformations must be registered before any of the tiles. Is there a better way to do this
        # than iterating through the list twice? I know this is a minor thing but it bothers me.
        for c in tag:  # .getchildren():
            if c.tag == "transformations":
                tileset.vflip = int(c.attrib.get("vflip", 0)) == 1
                tileset.hflip = int(c.attrib.get("hflip", 0)) == 1
                # - debug
                # print("Flip values: v={} h={}".format(tileset.vflip, tileset.hflip))

        for c in tag:  # .getchildren():
            # TODO: The tileset can only contain an "image" tag or multiple "tile" tags; it can't combine the two.
            # This should be enforced. For now, I'm just gonna support spritesheet tiles.
            if c.tag == "image":
                # create a tileset
                arg_sheet = c.attrib['source']
                tileset._add_image(folders, arg_sheet, num_tiles)

        return tileset

    @classmethod
    def fromjson(cls, folders, jdict, firstgid=None):
        print('[isometric.model] method .fromjson has been called')
        if 'source' in jdict:
            firstgid = int(jdict['firstgid'])
            srcc = jdict['source']

            # TODO: Another direct disk access here.
            if srcc.endswith(("tsx", "xml")):
                with open(os.path.join(*folders, srcc)) as f:
                    tag = ElementTree.fromstring(f.read())
                    return cls.fromxml(folders, tag, firstgid)
            elif srcc.endswith(("tsj", "json")):
                with open(os.path.join(*folders, srcc)) as f:
                    jdict = json.load(f)

        name = jdict['name']
        if firstgid is None:
            firstgid = int(jdict.get('firstgid', 1))
        tile_width = int(jdict['tilewidth'])
        tile_height = int(jdict['tileheight'])
        num_tiles = int(jdict['tilecount'])

        tileset = cls(name, tile_width, tile_height, firstgid)

        if "transformations" in jdict:
            c = jdict["transformations"]
            tileset.vflip = int(c.get("vflip", 0)) == 1
            tileset.hflip = int(c.get("hflip", 0)) == 1

        # TODO: The tileset can only contain an "image" tag or multiple "tile" tags; it can't combine the two.
        # This should be enforced. For now, I'm just gonna support spritesheet tiles.

        # create a tileset
        arg_sheet = jdict['image']
        tileset._add_image(folders, arg_sheet, num_tiles)

        return tileset


class IsometricMapObject:
    """
    A thing that can be placed on the map.
    """

    def __init__(self, **kwargs):
        self.name = ""
        # self.type = ""
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.gid = 0
        self.visible = 1

        self.properties = dict(kwargs)  # copy properties, stores various custom properties

        # super().__init__(**keywords)
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.drawingoffset = [0, 16]  # replaces the anchor stuff

    def __call__(self, dest_surface, sx, sy, mymap):
        """Draw this object at the requested surface coordinates on the provided surface."""
        if self.gid:
            tile_id = self.gid & NOT_ALL_FLAGS
            if tile_id > 0:
                my_tile = mymap.tilesets[tile_id]
                my_tile.paint_tile(dest_surface, sx+self.drawingoffset[0], sy+self.drawingoffset[1], self.gid & FLIPPED_HORIZONTALLY_FLAG, self.gid & FLIPPED_VERTICALLY_FLAG)

    @staticmethod
    def _deweirdify_coordinates(tx, ty, givenlayer):
        # It took ages to figure out the coordinate system that Tiled uses for objects on isometric maps. At first I
        # thought the pixel coordinate origin would be the upper left corner of the map's bounding box. It isn't.
        # In fact, it isn't a normal cartesian coordinate system at all. The pixel x,y values are the cell index
        # multiplied by the cell height. I cannot think of any situation for which this would be a useful way to store
        # pixel coordinates, but there you go.
        #
        # This function takes the Tiled pixel coordinates and changes them to tilemap cell coordinates. Feel free to
        # delete this long rant of a comment. Or leave it as a warning to others. I am just glad to finally understand
        # what's going on.

        mx = -0.5 + (tx / float(givenlayer.tile_height))
        my = -0.5 + (ty / float(givenlayer.tile_height))
        return mx, my

    @classmethod
    def fromxml(cls, tag, givenlayer):
        myob = cls()
        myob.name = tag.attrib.get("name")
        myob.type = tag.attrib.get(info_type_obj)
        # Convert the x,y pixel coordinates to x,y map coordinates.
        x = float(tag.attrib.get("x", 0))
        y = float(tag.attrib.get("y", 0))
        myob.x, myob.y = cls._deweirdify_coordinates(x, y, givenlayer)
        myob.gid = int(tag.attrib.get("gid"))
        myob.visible = int(tag.attrib.get("visible", 1))
        for t in tag:
            if t.tag == "properties":
                for p in t:
                    if p.tag == "property":
                        myob.properties[p.attrib.get("name", "property")] = p.attrib.get("value")
        return myob

    @classmethod
    def fromjson(cls, jdict, givenlayer):
        name = jdict.get("name")
        objtype = jdict.get(info_type_obj)
        # Convert the x,y pixel coordinates to x,y map coordinates.
        x, y = cls._deweirdify_coordinates(jdict.get("x", 0), jdict.get("y", 0), givenlayer)
        gid = jdict.get("gid")
        visible = jdict.get("visible")

        eproperties = dict()
        if "properties" in jdict:
            for p in jdict["properties"]:
                kk = p.get("name", "property")
                vv = p.get("value")
                eproperties[kk] = vv
        eproperties['name'] = name
        eproperties['type'] = objtype
        eproperties['x'], eproperties['y'] = x, y
        eproperties['gid'] = gid
        eproperties['visible'] = visible
        return cls(**eproperties)


class IsometricLayer:
    flag_csv = False

    def __init__(self, name, visible, map, offsetx=0, offsety=0):
        self.name = name
        self.visible = visible

        self.tile_width = map.tile_width
        self.tile_height = map.tile_height

        self.width = map.width
        self.height = map.height

        self.offsetx = offsetx
        self.offsety = offsety

        self.properties = {}
        self.cells = list()

    def __repr__(self):
        return '<Layer "%s" at 0x%x>' % (self.name, id(self))

    @classmethod
    def emptylayer(cls, name, givenmap):
        layer = cls(
            name, 0, givenmap, 0, 0
        )

        layer.cells = [0, ] * givenmap.height * givenmap.width

        return layer

    @classmethod
    def fromxml(cls, tag, givenmap):
        layer = cls(
            tag.attrib['name'], int(tag.attrib.get('visible', 1)), givenmap,
            int(tag.attrib.get('offsetx', 0)), int(tag.attrib.get('offsety', 0))
        )

        data = tag.find('data')
        if data is None:
            raise ValueError('layer %s does not contain <data>' % layer.name)

        data = data.text.strip()
        data = data.encode()  # Convert to bytes
        # Decode from base 64 and decompress via zlib
        data = decompress(b64decode(data))

        # I ran a test today and there's a slight speed advantage in leaving the cells as a list. It's not a big
        # advantage, but it's just as easy for now to leave the data as it is.
        #
        # I'm changing to a list from a tuple in case destructible terrain or modifiable terrain (such as doors) are
        # wanted in the future.
        layer.cells = list(struct.unpack('<%di' % (len(data) / 4,), data))
        assert len(layer.cells) == layer.width * layer.height

        return layer

    @classmethod
    def fromjson(cls, jdict, givenmap):
        layer = cls(
            jdict['name'], jdict.get('visible', True), givenmap,
            jdict.get('offsetx', 0), jdict.get('offsety', 0)
        )

        data = jdict.get('data')
        if data is None:
            raise ValueError('layer %s does not contain <data>' % layer.name)

        # Remark: (june 2022)
        # we need to support uncompressed data like CSV, for instance,
        # for specific use cases where the zlib module cannot be used
        # (hacking in the web ctx for example)

        if not cls.flag_csv:  # default mode -> data is compressed
            data = data.strip()
            data = data.encode()  # Convert to bytes
            # Decode from base 64 and decompress via zlib
            data = decompress(b64decode(data))
            # I ran a test today and there's a slight speed advantage in leaving the cells as a list.
            # It's not a big advantage, but it's just as easy for now to leave the data as it is.
            # I'm changing to a list from a tuple in case destructible terrain or modifiable terrain
            # (such as doors) ar wanted in the future
            layer.cells = list(struct.unpack('<%di' % (len(data) / 4,), data))
            assert len(layer.cells) == layer.width * layer.height
        else:  # uncompressed data
            layer.cells = data

        return layer

    def __len__(self):
        return self.height * self.width

    def _pos_to_index(self, x, y):
        # loop map feat.
        y = y % self.height
        x = x % self.width
        return y * self.width + x

    def __getitem__(self, key):
        x, y = key
        i = self._pos_to_index(x, y)
        # no test of boundaries bc of the loop map feat.
        # if 0 <= x < self.width and 0 <= y < self.height:
        return self.cells[i]

    def __setitem__(self, pos, value):
        x, y = pos
        i = self._pos_to_index(x, y)
        # if 0 <= x < self.width and 0 <= y < self.height:
        self.cells[i] = value


class ObjectGroup:
    def __init__(self, name, visible, offsetx, offsety):
        self.name = name
        self.visible = visible
        self.offsetx = offsetx
        self.offsety = offsety

        self.contents = list()

    @classmethod
    def fromxml(cls, tag, givenlayer, object_classes=None):
        mygroup = cls(
            tag.attrib['name'], int(tag.attrib.get('visible', 1)),
            int(tag.attrib.get('offsetx', 0)), int(tag.attrib.get('offsety', 0))
        )

        for t in tag:
            if t.tag == "object":
                if object_classes and t.attrib.get(info_type_obj) in object_classes:
                    myclass = object_classes[t.attrib.get(info_type_obj)]
                else:
                    myclass = IsometricMapObject
                mygroup.contents.append(myclass.fromxml(
                    t, givenlayer
                ))

        return mygroup

    @classmethod
    def fromjson(cls, folders, jdict, givenlayer, object_classes=None):
        mygroup = cls(
            jdict.get('name'), jdict.get('visible', True),
            jdict.get('offsetx', 0), jdict.get('offsety', 0)
        )

        if "objects" in jdict:
            for t in jdict["objects"]:
                if object_classes and t.get(info_type_obj) in object_classes:
                    myclass = object_classes[t.get(info_type_obj)]
                else:
                    myclass = IsometricMapObject
                mygroup.contents.append(myclass.fromjson(
                    t, givenlayer
                ))

        return mygroup


class IsometricMap:
    # Customization:
    # If a layer named "Move Layer" exists, the PC can only move into tiles that exist on this layer. The layer may be
    #   invisible.
    # If a layer named "Block Layer" exists, the PC cannot move into tiles that exist on this layer. The layer may be
    #   invisible.
    def __init__(self):
        self.tile_width = 0
        self.tile_height = 0
        self.width = 0
        self.height = 0
        self.layers = list()
        self.tilesets = _hub.tmx.data.Tilesets()
        self.objectgroups = dict()

        self.wrap_x = False
        self.wrap_y = False

        self.floor_layer = None
        self.wall_layer = None

        self.wallpaper = None
        self.mapname = None

    def seek_floor_and_wall(self):
        for n, layer in enumerate(self.layers):
            if layer.name == "Move Layer":
                self.floor_layer = n
            elif layer.name == "Block Layer":
                self.wall_layer = n

    @classmethod
    def load_tmx(cls, folders, filename, object_classes=None):
        # object_classes is a function that can parse a dict describing an object.
        # If None, the only objects that can be loaded are terrain objects.
        with open(os.path.join(*folders, filename)) as f:
            tminfo_tree = ElementTree.fromstring(f.read())

        # get most general map informations and create a surface
        tilemap = cls()

        tilemap.width = int(tminfo_tree.attrib['width'])
        tilemap.height = int(tminfo_tree.attrib['height'])
        tilemap.tile_width = int(tminfo_tree.attrib['tilewidth'])
        tilemap.tile_height = int(tminfo_tree.attrib['tileheight'])

        for tag in tminfo_tree.findall('tileset'):
            tilemap.tilesets.add(
                IsometricTileset.fromxml(folders, tag)
                # hacks work only if no more than 1 ts
            )

        for tag in tminfo_tree:
            if tag.tag == 'layer':
                layer = IsometricLayer.fromxml(tag, tilemap)
                tilemap.layers.append(layer)
            elif tag.tag == "objectgroup":
                if not tilemap.layers:
                    # If the first layer on the map is an objectgroup, this is gonna be a problem. Without
                    # a frame of reference, we won't be able to know what tile the object is in, and that is going
                    # to be important information. So, we add an empty layer with no offsets to act as this
                    # objectgroup's frame of reference.
                    tilemap.layers.append(IsometricLayer.emptylayer("The Mysterious Empty Layer", tilemap))
                tilemap.objectgroups[tilemap.layers[-1]] = ObjectGroup.fromxml(tag, tilemap.layers[-1], object_classes)
            elif tag.tag == "properties":
                for ptag in tag.findall("property"):
                    if ptag.get("name") == "wrap_x":
                        tilemap.wrap_x = ptag.get("value") == "true"
                    elif ptag.get("name") == "wrap_y":
                        tilemap.wrap_y = ptag.get("value") == "true"
                    elif ptag.get("name") == "mapname":
                        tilemap.mapname = ptag.get("mapname")
                    elif ptag.get("name") == "wallpaper":
                        tilemap.wallpaper = _hub.pygame.image.load(os.path.join("assets",ptag.get("value"))).convert_alpha()

        return tilemap

    @classmethod
    def load_json(cls, folders, filename, object_classes=None):
        # object_classes is a function that can parse a dict describing an object.
        # If None, the only objects that can be loaded are terrain objects.
        with open(os.path.join(*folders, filename)) as f:
            jdict = json.load(f)
        return cls.from_json_dict(folders, jdict, object_classes)

    @classmethod
    def from_json_dict(cls, folders, jdict, object_classes=None):
        # get most general map informations and create a surface
        tilemap = cls()

        tilemap.width = jdict['width']
        tilemap.height = jdict['height']
        tilemap.tile_width = jdict['tilewidth']
        tilemap.tile_height = jdict['tileheight']

        if "properties" in jdict:
            for tag in jdict["properties"]:
                if tag["name"] == "wrap_x":
                    tilemap.wrap_x = tag.get("value", False)
                elif tag["name"] == "wrap_y":
                    tilemap.wrap_y = tag.get("value", False)
                elif tag["name"] == "mapname":
                    tilemap.mapname = tag.get("value")
                elif tag["name"] == "wallpaper":
                    pprefix = os.pathsep.join(folders)
                    tilemap.wallpaper = _hub.pygame.image.load(os.path.join(pprefix, tag.get("value"))).convert_alpha()

        for tag in jdict['tilesets']:
            tilemap.tilesets.add(
                IsometricTileset.fromjson(folders, tag)
            )

        for tag in jdict["layers"]:
            if tag["type"] == 'tilelayer':
                layer = IsometricLayer.fromjson(tag, tilemap)
                tilemap.layers.append(layer)
            elif tag["type"] == "objectgroup":
                if not tilemap.layers:
                    # See above comment for why I'm adding an empty layer. TLDR: the objects need a reference frame.
                    tilemap.layers.append(IsometricLayer.emptylayer("The Mysterious Empty Layer", tilemap))
                tilemap.objectgroups[tilemap.layers[-1]] = ObjectGroup.fromjson(
                    folders, tag, tilemap.layers[-1], object_classes
                )
        return tilemap

    @classmethod
    def load(cls, folders, filename, object_classes=None):
        # - debug
        # print(_hub.bundle_name, folders)
        if not(filename.endswith(("tmx", "xml")) or filename.endswith(("tmj", "json"))):
            raise NotImplementedError(f"isometric.model -> No decoder available for map:{filename}")
        map_desc_format = 'tmx' if filename.endswith(("tmx", "xml")) else 'tmj'

        try:
            if 'tmj' == map_desc_format:
                mymap = cls.load_json(folders, filename, object_classes)
            else:
                mymap = cls.load_tmx(folders, filename, object_classes)
        except FileNotFoundError:
            # 2nd attempt, assuming we have to enter the bundle first
            folders.insert(0, _hub.bundle_name)
            if 'tmj' == map_desc_format:
                mymap = cls.load_json(folders, filename, object_classes)
            else:
                mymap = cls.load_tmx(folders, filename, object_classes)

        mymap.seek_floor_and_wall()
        return mymap

    def on_the_map(self, x, y):
        # Returns true if (x,y) is on the map, false otherwise
        return (self.wrap_x or ((x >= 0) and (x < self.width))) and (self.wrap_y or ((y >= 0) and (y < self.height)))

    def get_layer_by_name(self, layer_name):
        # The Layers type in Kengi supports indexing layers by name, but it
        # doesn't support accessing layers by
        # negative indices. I'm not sure that it supports slicing either. Anyhow, for now, only the map cursor needs
        # to look up layers by name so this function should be good enough for the time being.
        for lay in self.layers:
            if lay.name == layer_name:
                return lay

    def get_object_by_name(self, object_name):
        # Return the first object found with the provided name.
        for obgroup in self.objectgroups.values():
            for ob in obgroup.contents:
                if ob.name == object_name:
                    return ob

    def clamp_pos(self, pos):
        # For infinite scroll maps, clamp the x and/or y values
        nupos = list(pos)
        if self.wrap_x:
            f, i = math.modf(pos[0])
            nupos[0] = int(i) % self.width + f
        else:
            if pos[0] < 0:
                nupos[0] = 0
            elif pos[0] >= self.width:
                nupos[0] = self.width-1
        if self.wrap_y:
            f, i = math.modf(pos[1])
            nupos[1] = int(i) % self.height + f
        else:
            if pos[1] < 0:
                nupos[1] = 0
            elif pos[1] >= self.height:
                nupos[1] = self.height-1
        return tuple(nupos)

    def clamp_pos_int(self, pos):
        def spefilter(val):
            xinf, xmid, xsup = math.floor(val), math.floor(val) + 0.5, math.ceil(val)
            a, b, c = abs(val - xinf), abs(val - xmid), abs(val - xsup)
            if c < a:
                if c < b:
                    rez = xsup
                else:
                    rez = xmid
            else:
                if a < b:
                    rez = xinf
                else:
                    rez = xmid
            return rez

        # For infinite scroll maps, clamp the x and/or y values
        nupos = [math.floor(c) for c in pos]
        if self.wrap_x:
            f, i = math.modf(pos[0])
            nupos[0] = int(i) % self.width
        else:
            if pos[0] < 0:
                nupos[0] = 0
            elif pos[0] >= self.width:
                nupos[0] = self.width-1

        if self.wrap_y:
            f, i = math.modf(pos[1])
            nupos[1] = int(i) % self.height
        else:
            if pos[1] < 0:
                nupos[1] = 0
            elif pos[1] >= self.height:
                nupos[1] = self.height-1
        return tuple(nupos)

    def tile_is_blocked(self, x, y):
        pos = self.clamp_pos_int((x,y))
        if self.floor_layer is not None and self.layers[self.floor_layer][pos] == 0:
            return True
        if self.wall_layer is not None and self.layers[self.wall_layer][pos] != 0:
            return True
        else:
            return False
