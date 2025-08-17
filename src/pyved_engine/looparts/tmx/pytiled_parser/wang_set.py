"""This module contains a number of classes related to Wang Sets.

Wang Sets are the underlying data used by Tiled's terrain system.
See [Tiled's docs about terrain](https://doc.mapeditor.org/en/stable/manual/terrain/)
and also the [TMX Reference](https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#wangsets)
and the [JSON Reference](https://doc.mapeditor.org/en/stable/reference/json-map-format/#wang-set)
"""
from typing import Dict, List, Optional

import attr

from ..common_types import Color
from pytiled_parser.properties import Properties


@attr.s(auto_attribs=True)
class WangTile:
    """Defines a Wang tile by linking a tile in the tileset to a Wang ID.

    [TMX Reference](https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#wangtile)

    [JSON Reference](https://doc.mapeditor.org/en/stable/reference/json-map-format/#wang-tile)

    Attributes:
        tile_id: The ID of the tile this WangTile maps to
        wang_id: The wang color indexes for this tile. This is a list of IDs referring
            to colors within the wang set. In the order of top, top right, right,
            bottom right, bottom, bottom left, left, top left.
    """

    tile_id: int
    wang_id: List[int]


@attr.s(auto_attribs=True)
class WangColor:
    """A color that can be used to define the corner and/or edge of a Wang tile

    [TMX Reference](https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#wangcolor)

    [JSON Reference](https://doc.mapeditor.org/en/stable/reference/json-map-format/#wang-color)

    Attributes:
        color: An RGBA color used to identify this Wang color
        name: The name for this color
        probability: The probability used when randomizing tiles
        properties: The properties for this wang color
        class_: The Tiled class of this Wang Color
        tile: Tile ID of the tile representing this color
    """

    color: Color
    name: str
    probability: float
    tile: int
    class_: Optional[str] = None
    properties: Optional[Properties] = None


@attr.s(auto_attribs=True)
class WangSet:
    """A complete Wang Set defining a list of corner and edge
    [WangColors][pytiled_parser.wang_set.WangColor], and any number of
    [WangTiles][pytiled_parser.wang_set.WangTile]

    [TMX Reference](https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#wangset)

    [JSON Reference](https://doc.mapeditor.org/en/stable/reference/json-map-format/#wang-set)

    Attributes:
        name: Name of the WangSet
        properties: The properties for this wang set
        class_: The Tiled class of this Wang Set
        tile: Tile ID of the tile representing this Wang Set
        wang_colors: A list of [WangColors][pytiled_parser.wang_set.WangColor]
        wang_tiles: A list of [WangTiles][pytiled_parser.wang_set.WangTile]
        wang_type: A string noting the type of this wang set
    """

    name: str
    tile: int
    wang_type: str
    wang_tiles: Dict[int, WangTile]
    wang_colors: List[WangColor]
    class_: Optional[str] = None
    properties: Optional[Properties] = None
