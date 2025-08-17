import os
from pathlib import Path
from . import pytiled_parser
from ... import _hub
from ... import gfx

# game settings
# Ensure no partial squares with these values
WINDOW_WIDTH = 1024  # 16 * 64 or 32 * 32 or 64 * 16
WINDOW_HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
TILESIZE = 64
BLACK = (0, 0, 0)

kengi = _hub
pygame = kengi.pygame
TileLayerCls = pytiled_parser.layer.TileLayer
ObjLayerCls = pytiled_parser.layer.ObjectLayer


# By default, the collide method uses the default rect of the player.
# We create this custom method to compare the player's 'hit_rect' instead.
def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)


class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())  # ignore \n chars to avoid extra tiles on map

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE


class MapObj:
    def __init__(self):
        self.x = self.y = 0
        self.width = self.height = 0
        self.name = ''
        self.type = ''


class CustomTiledMap:
    def __init__(self, filename, tileset_path): #, filename):
        # tm = pytmx.load_pygame(filename, pixelAlpha=True)  # for transparency
        # LOCAL CtX
        outside_bundle = False
        try:
            tm_path = os.path.join('cartridge',filename)
            tm = pytiled_parser.parse_map(tm_path)
        except FileNotFoundError:
            outside_bundle = True
            print(_hub.bundle_name)
            tm_path = os.path.join(_hub.bundle_name,'cartridge',filename)
            tm = pytiled_parser.parse_map(tm_path)

        # WEB
        # tm = pytiled_parser.parse_map(filename)
        tilew, tileh = tm.tile_size
        self.tile_size = (tilew, tileh)

        mapw, maph = tm.map_size
        self.width = mapw * tilew
        self.height = maph * tileh
        self.tmxdata = tm

        self.objects = list()  # loaded objects. Need to have attr: x, y, width, height, name, type
        self._populate_obj()

        # init my_tileset/ self.ts.
        # /!\ here we support only ONE tileset
        my_tileset = None
        for firstgid, obj in tm.tilesets.items():
            self.firstgid = firstgid
            # print(obj.image.as_posix())
            if outside_bundle:
                sheet_path = os.path.join(_hub.bundle_name, 'cartridge', obj.image.as_posix())
            else:
                sheet_path = os.path.join('cartridge', obj.image.as_posix())
            new_sprsheet = gfx.Spritesheet(sheet_path)  # gpath+ '/' + obj.image.as_posix() )

            # hot fix suite au massacre de pytiled_parser (retrait brutal attr)
            if not isinstance(obj.spacing, int):
                spp = obj.spacing[0]
            else:
                spp = obj.spacing
            # -- done

            new_sprsheet.set_infos(
                (obj.tile_width, obj.tile_height),
                obj.tile_count,
                obj.columns,
                spp
            )
            my_tileset = new_sprsheet
            break

        self.ts = my_tileset

        # ! super important! #  GAMECHANGER!!!!!
        for pimg in self.ts.cache.values():
            pimg.set_colorkey(BLACK)

    def _populate_obj(self):
        ref_objlayer = None
        for elt in self.tmxdata.layers:
            if isinstance(elt, ObjLayerCls):
                ref_objlayer = elt
                for obj_elt in ref_objlayer.tiled_objects:
                    mo = MapObj()
                    mo.name = obj_elt.name
                    mo.x, mo.y = obj_elt.coordinates
                    mo.type = obj_elt.class_
                    mo.width, mo.height = obj_elt.size
                    self.objects.append(mo)
                    print(mo.name, mo.type, mo.x, mo.y, mo.width, mo.height)
                break
        if not ref_objlayer:
            raise ValueError('no object layer found in the provided tmx/tmj map!')

    def render(self, surface):
        # get tile image by id used in the tmx file

        for layer in self.tmxdata.layers:
            if not isinstance(layer, ObjLayerCls):
                layerw, layerh = layer.size
                for j in range(layerh):
                    for i in range(layerw):  # iterate over all tiles...
                        tilerank = layer.data[j][i] - self.firstgid  # <-> (gid - firsgid)
                        tile_img = None
                        if tilerank >= self.ts.card:
                            print('**warning** ignored tilerank:', tilerank)
                        elif tilerank >= 0:
                            tile_img = self.ts[tilerank]
                        if tile_img:
                            surface.blit(tile_img, (i * self.tile_size[0], j * self.tile_size[1]))

    def make_map(self):
        temp_surface = pygame.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply_sprite(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(WINDOW_WIDTH / 2)
        y = -target.rect.centery + int(WINDOW_HEIGHT / 2)

        # limit scrolling to map size
        x = min(0, x)  # left hand side
        y = min(0, y)  # top
        x = max(-(self.width - WINDOW_WIDTH), x)  # right side
        y = max(-(self.height - WINDOW_HEIGHT), y)  # bottom
        self.camera = pygame.Rect(x, y, self.width, self.height)
