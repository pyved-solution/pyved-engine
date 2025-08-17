"""The tiled_map module contains the primary TiledMap class which represents a single
map from Tiled.
"""

from pathlib import Path
from typing import Dict, List, Optional
from .common_types import Color, OrderedPair, Size
from .layer import Layer
from .properties import Properties
from .tileset import Tileset


TilesetDict = Dict[int, Tileset]


class TiledMap:
    """Object for storing a Tiled map with all associated objects.

    This object is the top level object for a map. It contains all layers within a map,
    as well as all Tiesets used by the map. When creating an implementation, this will
    be the primary class to work with to pull all data relating to a map.

    `TMX Reference <https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#map>`_

    `JSON Reference <https://doc.mapeditor.org/en/stable/reference/json-map-format/#map>`_

    Attributes:
        infinite: If the map is infinite or not.
        layers: List of layer objects by draw order.
        map_size: The map width in tiles.
        next_layer_id: Stores the next available ID for new layers.
        next_object_id: Stores the next available ID for new objects.
        orientation: Map orientation. Tiled supports "orthogonal", "isometric",
            "staggered" and "hexagonal"
        render_order: The order in which tiles on tile layers are rendered. Valid values
            are right-down, right-up, left-down and left-up. In all cases, the map is
            drawn row-by-row. (only supported for orthogonal maps at the moment)
        tiled_version: The Tiled version used to save the file. May be a date (for
            snapshot builds).
        tile_size: The size of a tile.
        tilesets: Dict of Tileset where Key is the firstgid and the value is the Tileset
        version: The JSON format version.
        background_color: The background color of the map.
        properties: The properties of the Map.
        hex_side_length: Only for hexagonal maps. Determines the width or height
            (depending on the staggered axis) of the tile's edge, in pixels.
        stagger_axis: For staggered and hexagonal maps, determines which axis ("x" or
            "y") is staggered.
        stagger_index: For staggered and hexagonal maps, determines whether the "even"
            or "odd" indexes along the staggered axis are shifted.
        class_: The Tiled class of this Map.
        parallax_origin: The point on the map to center the parallax scrolling of layers on.
    """
    def __init__(self, **kwars):
        for k,v in kwars.items():
            setattr(self, k, v)
        # infinite: bool
        # layers: List[Layer]
        # map_size: Size
        # next_layer_id: Optional[int]
        # next_object_id: int
        # orientation: str
        # render_order: str
        # tiled_version: str
        # tile_size: Size
        # tilesets: TilesetDict
        # version: str
        #
        # parallax_origin: OrderedPair = OrderedPair(0, 0)
        #
        # map_file: Optional[Path] = None
        # class_: Optional[str] = None
        # background_color: Optional[Color] = None
        # properties: Optional[Properties] = None
        # hex_side_length: Optional[int] = None
        # stagger_axis: Optional[str] = None
        # stagger_index: Optional[str] = None
