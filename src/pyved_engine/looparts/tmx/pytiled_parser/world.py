"""This module provides an implementation for World files from Tiled.

See [Tiled's docs for Worlds](https://doc.mapeditor.org/en/stable/manual/worlds/)
for more info about worlds and how to use them.

The functionality within PyTiled Parser is to load the world and outline the size
and position of each map, and provide the path to the map file. Loading a world
does not automatically load each map within the world, this is so that the game
or engine implementation can decide how to handle map loading.
"""

import json
import re
from os import listdir
from os.path import isfile, join
from pathlib import Path
from typing import List

# from typing_extensions import TypedDict
from .common_types import OrderedPair, Size


class WorldMap:
    """Represents a map within a world.

    This object can be accessed to load in a map after loading the world.

    This class translates to each object within the `maps` list of a
    World file

    Attributes:
        map_file: A Path object to the map file, can be passed to
            the pytiled_parser.parse_map function later.
        size: The size of the map in pixels
        coordinates: The position of the map within the world in pixels
    """

    map_file: Path
    size: Size
    coordinates: OrderedPair


class World:
    """Represents a world file.

    Attributes:
        maps: The list of maps within the world. These are not fully parsed
            TiledMap objects, but rather WorldMap objects which can be used
            to later parse each individual map.
        only_show_adjacent: Largely only used by the Tiled editor to determine
            if only maps adjacent to the active one should be displayed. This
            could be used to determine implementation behavior as well though
            to toggle auto-loading of adjacent maps or something of the sort.
    """

    maps: List[WorldMap]
    only_show_adjacent: bool = False


# class RawPattern(TypedDict):
#     regexp: str
#     multiplierX: float
#     multiplierY: float
#     offsetX: float
#     offsetY: float
#
#
# class RawWorldMap(TypedDict):
#     fileName: str
#     height: float
#     width: float
#     x: float
#     y: float
#
#
# class RawWorld(TypedDict):
#     maps: List[RawWorldMap]
#     patterns: List[RawPattern]
#     onlyShowAdjacentMaps: bool


def _parse_world_map(raw_world_map, map_file: Path) -> WorldMap:  # raw_world_map: RawWorldMap
    """Parse the RawWorldMap into a WorldMap.

    Args:
        raw_world_map: The RawWorldMap to parse
        map_file: The file of tiled_map to parse

    Returns:
        WorldMap: The parsed WorldMap object
    """
    return WorldMap(
        map_file=map_file,
        size=Size(raw_world_map["width"], raw_world_map["height"]),
        coordinates=OrderedPair(raw_world_map["x"], raw_world_map["y"]),
    )


def parse_world(file: Path) -> World:
    """Parse the raw world into a pytiled_parser type

    Args:
        file: Path to the world's file

    Returns:
        World: A properly parsed [World][pytiled_parser.world.World]
    """

    with open(file) as world_file:
        raw_world = json.load(world_file)

    parent_dir = file.parent

    maps: List[WorldMap] = []

    if raw_world.get("maps"):
        for raw_map in raw_world["maps"]:
            map_path = Path(parent_dir / raw_map["fileName"])
            maps.append(_parse_world_map(raw_map, map_path))

    if raw_world.get("patterns"):
        for raw_pattern in raw_world["patterns"]:
            regex = re.compile(raw_pattern["regexp"])
            map_files = [
                f
                for f in listdir(parent_dir)
                if isfile(join(parent_dir, f)) and regex.match(f)
            ]
            for map_file in map_files:
                search = regex.search(map_file)
                if search:
                    width = raw_pattern["multiplierX"]
                    height = raw_pattern["multiplierY"]

                    offset_x = 0
                    offset_y = 0

                    if raw_pattern.get("offsetX"):
                        offset_x = raw_pattern["offsetX"]

                    if raw_pattern.get("offsetY"):
                        offset_y = raw_pattern["offsetY"]

                    x = (float(search.group(1)) * width) + offset_x
                    y = (float(search.group(2)) * height) + offset_y

                    raw_world_map = {  # raw_world_map : RawWorldMap
                        "fileName": map_file,
                        "width": width,
                        "height": height,
                        "x": x,
                        "y": y,
                    }

                    map_path = Path(parent_dir / map_file)
                    maps.append(_parse_world_map(raw_world_map, map_path))

    world = World(maps=maps)

    if raw_world.get("onlyShowAdjacentMaps"):
        world.only_show_adjacent = raw_world["onlyShowAdjacentMaps"]

    return world
