"""Provides an interface for Tilesets and the various objects within them.

Also see [Tiled's Docs for Editing Tilesets](https://doc.mapeditor.org/en/stable/manual/editing-tilesets/)
and [TMX Reference](https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#tileset)
and [JSON Reference](https://doc.mapeditor.org/en/stable/reference/json-map-format/#tileset)
"""
# pylint: disable=too-few-public-methods
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional

from . import layer
from . import properties as properties_
from .common_types import Color, OrderedPair


# from .wang_set import WangSet


class Grid(NamedTuple):
    """Contains info used in isometric maps.

    This element is only used in case of isometric orientation, and determines how tile
    overlays for terrain and collision information are rendered.

    `TMX Reference <https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#tmx-grid>`_

    `JSON Reference <https://doc.mapeditor.org/en/stable/reference/json-map-format/#grid>`_

    Attributes:
        orientation: Orientation of the grid for the tiles in this tileset (orthogonal
            or isometric).
        width: Width of a grid cell.
        height: Height of a grid cell.
    """

    orientation: str
    width: int
    height: int


class Frame(NamedTuple):
    """Animation Frame object.

    This is only used as a part of an animation for Tile objects. A frame simply points
    to a tile within the tileset, and gives a duration. Meaning that tile would be
    displayed for the given duration.

    `TMX Reference <https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#tmx-frame>`_

    `JSON Reference <https://doc.mapeditor.org/en/stable/reference/json-map-format/#json-frame>`_

    Attributes:
        tile_id: The local ID of a tile within the parent tile set object.
        duration: How long in milliseconds this frame should be displayed before
            advancing to the next frame.
    """

    tile_id: int
    duration: int


class Transformations:
    """Transformations Object.

    This is used to store what transformations may be performed on Tiles
    within a tileset. Within Tiled this primarily used with wang sets and
    the terrain system, however, could be used for any means a game/engine
    wants to really.

    `TMX Reference <https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#transformations>`_

    `JSON Reference <https://doc.mapeditor.org/en/stable/reference/json-map-format/#transformations>`_

    Attributes:
        hflip: Allow horizontal flip?
        vflip: Allow vertical flip?
        rotate: Allow rotation?
        prefer_untransformed: Should untransformed tiles be preferred?
    """

    hflip: bool = False
    vflip: bool = False
    rotate: bool = False
    prefer_untransformed: bool = False


class Tile:
    """Individual tile object.

    This class more closely resembles the JSON format than TMX. A number of values
    within this class in the TMX format are pulled into other sub-tags such as <image>.

    `TMX Reference <https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#tile>`_

    `JSON Reference <https://doc.mapeditor.org/en/stable/reference/json-map-format/#tile-definition>`_

    Attributes:
        id: The local tile ID within it's tileset.
        opacity: The opacity this Tiled should be rendered with.
        type: An optional, arbitrary string that can be used to denote different
            types of tiles. For example "wall" or "floor".
        animation: A list of [Frame][pytiled_parser.tileset.Frame] objects which
            makeup the animation for an animated tile.
        objects: An [ObjectLayer][pytiled_parser.layer.ObjectLayer] which contains
            objects that can be used for custom collision on the Tile. This field
            is set by the Tile Collision editor in Tiled.
        image: A path to the image for this tile.
        image_width: The width of this tile's image.
        image_height: The height of this tile's image.
        properties: A list of properties on this Tile.
        tileset: The [Tileset][pytiled_parser.tileset.Tileset] this tile came from.
        flipped_horizontally: Should this Tile be flipped horizontally?
        flipped_diagonally: Should this Tile be flipped diagonally?
        flipped_vertically: Should this Tile be flipped vertically?
        class_: The Tiled class of this Tile.
    """

    id: int
    opacity: int = 1
    x: int = 0
    y: int = 0
    width: Optional[int] = None
    height: Optional[int] = None
    class_: Optional[str] = None
    animation: Optional[List[Frame]] = None
    objects: Optional[layer.Layer] = None
    image: Optional[Path] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    properties: Optional[properties_.Properties] = None
    tileset: Optional["Tileset"] = None
    flipped_horizontally: bool = False
    flipped_diagonally: bool = False
    flipped_vertically: bool = False


class Tileset:
    """A Tileset is a collection of tiles.

    This class much more closely resembles the JSON format than TMX.

    `TMX Reference <https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#tileset>`_

    `JSON Reference <https://doc.mapeditor.org/en/stable/reference/json-map-format/#tileset>`_

    Attributes:
        name: The name of this tileset.
        tile_width: The width of a tile in this tileset in pixels.
        tile_height: The height of a tile in this tileset in pixels.
        tile_count: The number of tiles in this tileset.
        columns: The number of tile columns in the tileset. For image collection
            tilesets it is editable and is used when displaying the tileset.
        firstgid: The global ID to give to the first Tile in this tileset. Global IDs
            for the rest of the tiles will increment from this number.
        spacing: The spacing in pixels between the tiles in this tileset (applies to
            the tileset image).
        type: Will always be `tileset`. Is statically included as a way to determine the
            type of a JSON file since Tiled does not have different extesnsions for map
            and tileset JSON files(as opposed to TMX/TSX files). This value will typically not be used.
        spacing: Spacing between adjacent tiles in the image in pixels. Defaults to 0.
        margin: Buffer between the image edge and the first tile in the image in pixels. Defaults to 0.
        tiled_version: The version of Tiled this tileset was saved with
        version: The version of the JSON or TSX format this tileset was saved with.
            This will typically be the same as the tiled_version parameter, but they are tracked separately
            mostly for futureproofing.
        image: The image file to be used for spritesheet tile sets.
        image_width: The width of the `image` in pixels. Only set if the image parameter is.
            This value is taken from whatever Tiled outputs, the image size is not calculated by pytiled-parser.
        image_height: The height of the `image` in pixels. Only set if the image parameter is.
            This value is taken from whatever Tiled outputs, the image size is not calculated by pytiled-parser.
        transformations: What types of transformations are allowed on tiles within
            this Tileset
        background_color: The background color of the tileset. This will typically only be
            used by the editor, but could be useful for displaying a TileSet if you had the need to do that.
        tileoffset: Used to specify an offset in pixels when drawing a tile from the
            tileset. When not present, no offset is applied.
        transparent_color: A color that should act as transparent on any tiles within the
            tileset. This would need to be taken into account by an implementation when loading the tile images.
        grid: Only used in case of isometric orientation, and determines how tile
            overlays for terrain and collision information are rendered.
        properties: The properties for this Tileset.
        tiles: Dict of Tile objects with the Tile.id value as the key.
        wang_sets: List of WangSets, this is used by the terrain system in Tiled. It is unlikely an
            implementation in a game engine would need to use these values.
        alignment: Which alignment to use for tile objects from this tileset.
        class_: The Tiled class of this TileSet.
        tile_render_size: The size to use when rendering tiles from this tileset. Can be either "tile" or "grid".
        fill_mode: The fill mode to use when rendering tiles from this tileset.
            Can be either "stretch" or "preserve-aspect-fit".
    """

    def __init__(self,
                 name='',
                 tile_width=0,
                 tile_height=0,
                 tile_count=0,
                 columns=0,
                 firstgid=0,
                 type="tileset",
                 tile_render_size="tile",
                 fill_mode="stretch",
                 spacing=0,
                 margin=0,
                 tiled_version=None,
                 version=None,
                 image=None,
                 image_width=None,
                 image_height=None,
                 transformations=None,
                 class_=None,
                 background_color=None,
                 tileoffset=None,
                 transparent_color=None,
                 grid=None,
                 properties=None,
                 tiles=None,
                 wang_sets=None,  # Optional[List[WangSet]] = None
                 alignment=None,
                 ):
        self.name = name
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.tile_count = tile_count
        self.columns = columns
        self.firstgid = firstgid
        self.type = type
        self.tile_render_size = tile_render_size
        self.fill_mode = fill_mode
        self.spacing = spacing,
        self.margin = margin
        self.tiled_version = tiled_version
        self.version = version
        self.image = image
        self.image_width = image_width
        self.image_height = image_height
        self.transformations = transformations
        self.class_ = class_
        self.background_color = background_color
        self.tileoffset = tileoffset
        self.transparent_color = transparent_color
        self.grid = grid
        self.properties = properties
        self.tiles = tiles
        self.wang_sets = wang_sets
        self.alignment = alignment
