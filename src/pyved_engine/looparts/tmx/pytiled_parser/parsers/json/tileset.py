from pathlib import Path
from typing import List, Optional, Union
# from typing_extensions import TypedDict
from ...common_types import OrderedPair
# from pytiled_parser.parsers.json.layer import RawLayer
from ...parsers.json.layer import parse as parse_layer
# from pytiled_parser.parsers.json.properties import RawProperty
from ...parsers.json.properties import parse as parse_properties
# from pytiled_parser.parsers.json.wang_set import RawWangSet
# from pytiled_parser.parsers.json.wang_set import parse as parse_wangset
from ...tileset import Frame, Grid, Tile, Tileset, Transformations
from ...util import parse_color


# RawFrame = TypedDict("RawFrame", {"duration": int, "tileid": int})
# RawFrame.__doc__ = """
#     The keys and their types that appear in a Frame JSON Object.
# """


# RawTileOffset = TypedDict("RawTileOffset", {"x": int, "y": int})
# RawTileOffset.__doc__ = """
#     The keys and their types that appear in a TileOffset JSON Object.
# """


# RawTransformations = TypedDict(
#     "RawTransformations",
#     {"hflip": bool, "vflip": bool, "rotate": bool, "preferuntransformed": bool},
# )
# RawTransformations.__doc__ = """
#     The keys and their types that appear in a Transformations JSON Object.
# """


# RawTile = TypedDict(
#     "RawTile",
#     {
#         "animation": List[RawFrame],
#         "class": str,
#         "id": int,
#         "image": str,
#         "imageheight": int,
#         "imagewidth": int,
#         "opacity": float,
#         "type": str,
#         "properties": List[RawProperty],
#         "objectgroup": RawLayer,
#         "x": int,
#         "y": int,
#         "width": int,
#         "height": int,
#     },
# )
# RawTile.__doc__ = """
#     The keys and their types that appear in a Tile JSON Object.
# """


# RawGrid = TypedDict("RawGrid", {"height": int, "width": int, "orientation": str})
# RawGrid.__doc__ = """
#     The keys and their types that appear in a Grid JSON Object.
# """


# RawTileSet = TypedDict(
#     "RawTileSet",
#     {
#         "backgroundcolor": str,
#         "class": str,
#         "columns": int,
#         "firstgid": int,
#         "grid": RawGrid,
#         "image": str,
#         "imageheight": int,
#         "imagewidth": int,
#         "margin": int,
#         "name": str,
#         "properties": List[RawProperty],
#         "fillmode": str,
#         "objectalignment": str,
#         "source": str,
#         "spacing": int,
#         "tilecount": int,
#         "tiledversion": str,
#         "tileheight": int,
#         "tileoffset": RawTileOffset,
#         "tilerendersize": str,
#         "tiles": List[RawTile],
#         "tilewidth": int,
#         "transparentcolor": str,
#         "transformations": RawTransformations,
#         "version": Union[str, float],
#         "wangsets": List[RawWangSet],
#     },
# )
# RawTileSet.__doc__ = """
#     The keys and their types that appear in a TileSet JSON Object.
# """


def _parse_frame(raw_frame):  #: RawFrame) -> Frame:
    """Parse the raw_frame to a Frame.

    Args:
        raw_frame: RawFrame to be parsed to a Frame

    Returns:
        Frame: The Frame created from the raw_frame
    """

    return Frame(duration=raw_frame["duration"], tile_id=raw_frame["tileid"])


def _parse_tile_offset(raw_tile_offset):  # : RawTileOffset) -> OrderedPair:
    """Parse the raw_tile_offset to an OrderedPair.

    Args:
        raw_tile_offset: RawTileOffset to be parsed to an OrderedPair

    Returns:
        OrderedPair: The OrderedPair created from the raw_tile_offset
    """

    return OrderedPair(raw_tile_offset["x"], raw_tile_offset["y"])


def _parse_transformations(raw_transformations):  #: RawTransformations) -> Transformations:
    """Parse the raw_transformations to a Transformations object.

    Args:
        raw_transformations: RawTransformations to be parsed to a Transformations

    Returns:
        Transformations: The Transformations created from the raw_transformations
    """

    return Transformations(
        hflip=raw_transformations["hflip"],
        vflip=raw_transformations["vflip"],
        rotate=raw_transformations["rotate"],
        prefer_untransformed=raw_transformations["preferuntransformed"],
    )


def _parse_grid(raw_grid) -> Grid:  #raw_grid : RawGrid
    """Parse the raw_grid to a Grid object.

    Args:
        raw_grid: RawGrid to be parsed to a Grid

    Returns:
        Grid: The Grid created from the raw_grid
    """

    return Grid(
        orientation=raw_grid["orientation"],
        width=raw_grid["width"],
        height=raw_grid["height"],
    )


def _parse_tile(raw_tile, external_path: Optional[Path] = None) -> Tile:  #raw_tile: RawTile
    """Parse the raw_tile to a Tile object.

    Args:
        raw_tile: RawTile to be parsed to a Tile

    Returns:
        Tile: The Tile created from the raw_tile
    """

    id_ = raw_tile["id"]
    tile = Tile(id=id_)

    if raw_tile.get("animation") is not None:
        tile.animation = []
        for frame in raw_tile["animation"]:
            tile.animation.append(_parse_frame(frame))

    if raw_tile.get("objectgroup") is not None:
        tile.objects = parse_layer(raw_tile["objectgroup"])

    if raw_tile.get("properties") is not None:
        tile.properties = parse_properties(raw_tile["properties"])

    if raw_tile.get("image") is not None:
        if external_path:
            tile.image = Path(external_path / raw_tile["image"]).absolute().resolve()
        else:
            tile.image = Path(raw_tile["image"])

    # These are ignored from coverage because there does not exist a scenario where
    # image is set, but these aren't, so the branches will never fully be hit.
    # However, leaving these checks in place is nice to prevent fatal errors on
    # a manually edited map that has an "incorrect" but not "unusable" structure
    #
    # We also set the width and height attributes here as the values for these in
    # Tiled defaults to the same value as imagewidth and imageheight if no custom value
    # is set. We then later load in the custom value if it exists.
    if raw_tile.get("imagewidth") is not None:  # pragma: no cover
        tile.image_width = raw_tile["imagewidth"]
        tile.width = tile.image_width

    if raw_tile.get("imageheight") is not None:  # pragma: no cover
        tile.image_height = raw_tile["imageheight"]
        tile.height = tile.image_height

    if raw_tile.get("type") is not None:
        tile.class_ = raw_tile["type"]

    if raw_tile.get("class") is not None:
        tile.class_ = raw_tile["class"]

    if raw_tile.get("x") is not None:
        tile.x = raw_tile["x"]

    if raw_tile.get("y") is not None:
        tile.y = raw_tile["y"]

    if raw_tile.get("width") is not None:
        tile.width = raw_tile["width"]

    if raw_tile.get("height") is not None:
        tile.height = raw_tile["height"]

    return tile


def parse(
    raw_tileset, # : RawTileSet,
    firstgid: int,
    external_path: Optional[Path] = None,
) -> Tileset:
    """Parse the raw tileset into a pytiled_parser type

    Args:
        raw_tileset: Raw Tileset to be parsed.
        firstgid: GID corresponding the first tile in the set.
        external_path: The path to the tileset if it is not an embedded one.

    Returns:
        TileSet: a properly typed TileSet.
    """

    tileset = Tileset(
        name=raw_tileset["name"],
        tile_count=raw_tileset["tilecount"],
        tile_width=raw_tileset["tilewidth"],
        tile_height=raw_tileset["tileheight"],
        columns=raw_tileset["columns"],
        spacing=raw_tileset["spacing"],
        margin=raw_tileset["margin"],
        firstgid=firstgid,
    )

    if raw_tileset.get("version") is not None:
        # This is here to support old versions of Tiled Maps. It's a pain
        # to keep old versions in the test data and not update them with the
        # rest so I'm excluding this from coverage. In reality it's probably
        # not needed. Tiled hasn't been using floats for the version for a long time
        if isinstance(raw_tileset["version"], float):  # pragma: no cover
            tileset.version = str(raw_tileset["version"])
        else:
            tileset.version = raw_tileset["version"]

    if raw_tileset.get("tiledversion") is not None:
        tileset.tiled_version = raw_tileset["tiledversion"]

    if raw_tileset.get("image") is not None:
        if external_path:
            tileset.image = (
                Path(external_path / raw_tileset["image"]).absolute().resolve()
            )
        else:
            tileset.image = Path(raw_tileset["image"])

    # See above note about imagewidth and imageheight on parse_tile function
    # for an explanation on why these are ignored
    if raw_tileset.get("imagewidth") is not None:  # pragma: no cover
        tileset.image_width = raw_tileset["imagewidth"]

    if raw_tileset.get("imageheight") is not None:  # pragma: no cover
        tileset.image_height = raw_tileset["imageheight"]

    if raw_tileset.get("objectalignment") is not None:
        tileset.alignment = raw_tileset["objectalignment"]

    if raw_tileset.get("backgroundcolor") is not None:
        tileset.background_color = parse_color(raw_tileset["backgroundcolor"])

    if raw_tileset.get("tileoffset") is not None:
        tileset.tile_offset = _parse_tile_offset(raw_tileset["tileoffset"])

    if raw_tileset.get("transparentcolor") is not None:
        tileset.transparent_color = parse_color(raw_tileset["transparentcolor"])

    if raw_tileset.get("grid") is not None:
        tileset.grid = _parse_grid(raw_tileset["grid"])

    if raw_tileset.get("properties") is not None:
        tileset.properties = parse_properties(raw_tileset["properties"])

    if raw_tileset.get("tiles") is not None:
        tiles = {}
        for raw_tile in raw_tileset["tiles"]:
            tiles[raw_tile["id"]] = _parse_tile(raw_tile, external_path=external_path)
        tileset.tiles = tiles

    if raw_tileset.get("wangsets") is not None:
        print('*** WARN: wangsets not supported by this PARSER ***')
        wangsets = []
        # for raw_wangset in raw_tileset["wangsets"]:
        #     wangsets.append(parse_wangset(raw_wangset))
        tileset.wang_sets = wangsets

    if raw_tileset.get("transformations") is not None:
        tileset.transformations = _parse_transformations(raw_tileset["transformations"])

    if raw_tileset.get("class") is not None:
        tileset.class_ = raw_tileset["class"]

    if raw_tileset.get("tilerendersize") is not None:
        tileset.tile_render_size = raw_tileset["tilerendersize"]

    if raw_tileset.get("fillmode") is not None:
        tileset.fill_mode = raw_tileset["fillmode"]

    return tileset
