import json
import xml.etree.ElementTree as etree
from pathlib import Path
from typing import List, Union, cast
# from typing_extensions import TypedDict
from ...common_types import OrderedPair, Size
from ...exception import UnknownFormat
# from pytiled_parser.parsers.json.layer import RawLayer
from .layer import parse as parse_layer
# from pytiled_parser.parsers.json.properties import RawProperty
from .properties import parse as parse_properties
# from pytiled_parser.parsers.json.tileset import RawTileSet
from .tileset import parse as parse_json_tileset
from ...parsers.tmx.tileset import parse as parse_tmx_tileset
from ...tiled_map import TiledMap, TilesetDict
from ...util import check_format, parse_color

# RawTilesetMapping = TypedDict("RawTilesetMapping", {"firstgid": int, "source": str})
RawTilesetMapping = {
    'firstgid': 0,
    'source': ''
}

RawTiledMap = {
    "backgroundcolor": '',
    "compressionlevel": 0,
    "height": 0,
    "hexsidelength": 0,
    "infinite": False,
    "layers": list(),
    "nextlayerid": 0,
    "nextobjectid": 0,
    "orientation": '',
    "properties": list(),
    "renderorder": '',
    "staggeraxis": '',
    "staggerindex": '',
    "tiledversion": '',
    "tileheight": 0,
    "tilesets": list(),
    "tilewidth": 0,
    "class": '',
    "type": '',
    "version": '',
    "width": 0,
    "parallaxoriginx": 0.0,
    "parallaxoriginy": 0.0,
}

# RawTiledMap = TypedDict(
#     "RawTiledMap",
#     {
#         "backgroundcolor": str,
#         "compressionlevel": int,
#         "height": int,
#         "hexsidelength": int,
#         "infinite": bool,
#         "layers": List[RawLayer],
#         "nextlayerid": int,
#         "nextobjectid": int,
#         "orientation": str,
#         "properties": List[RawProperty],
#         "renderorder": str,
#         "staggeraxis": str,
#         "staggerindex": str,
#         "tiledversion": str,
#         "tileheight": int,
#         "tilesets": List[RawTilesetMapping],
#         "tilewidth": int,
#         "class": str,
#         "type": str,
#         "version": Union[str, float],
#         "width": int,
#         "parallaxoriginx": float,
#         "parallaxoriginy": float,
#     },
# )
# RawTiledMap.__doc__ = """
#     The keys and their types that appear in a Tiled JSON Map Object.
#
#     Tiled Docs: https://doc.mapeditor.org/en/stable/reference/json-map-format/#map
# """


def parse(file: Path) -> TiledMap:
    """Parse the raw Tiled map into a pytiled_parser type.

    Args:
        file: Path to the map file.

    Returns:
        TiledMap: A parsed TiledMap.
    """
    with open(file) as map_file:
        raw_tiled_map = json.load(map_file)

    #before ktg
    #parent_dir = file.parent
    # ktg: we assume tileset is ALWAYS embedded!
    parent_dir='.'

    #before ktg:
    # raw_tilesets: List[Union[RawTileSet, RawTilesetMapping]] = raw_tiled_map["tilesets"]
    raw_tilesets = raw_tiled_map['tilesets']
    #before ktg
    # tilesets: TilesetDict = {}
    tilesets = {}

    for raw_tileset in raw_tilesets:
        if raw_tileset.get("source") is not None:
            # Is an external Tileset
            tileset_path = Path(parent_dir / raw_tileset["source"])
            parser = check_format(tileset_path)
            with open(tileset_path) as raw_tileset_file:
                if parser == "tmx":
                    raw_tileset_external = etree.parse(raw_tileset_file).getroot()
                    tilesets[raw_tileset["firstgid"]] = parse_tmx_tileset(
                        raw_tileset_external,
                        raw_tileset["firstgid"],
                        external_path=tileset_path.parent,
                    )
                else:
                    try:
                        tilesets[raw_tileset["firstgid"]] = parse_json_tileset(
                            json.load(raw_tileset_file),
                            raw_tileset["firstgid"],
                            external_path=tileset_path.parent,
                        )
                    except ValueError:
                        raise UnknownFormat(
                            "Unknown Tileset Format, please use either the TSX or JSON format. "
                            "This message could also mean your tileset file is invalid or corrupted."
                        )
        else:
            # Is an embedded Tileset
            # raw_tileset = cast(RawTileSet, raw_tileset)
            tilesets[raw_tileset["firstgid"]] = parse_json_tileset(
                raw_tileset, raw_tileset["firstgid"]
            )

    if isinstance(raw_tiled_map["version"], float):  # pragma: no cover
        version = str(raw_tiled_map["version"])
    else:
        version = raw_tiled_map["version"]

    # `map` is a built-in function
    map_ = TiledMap(
        map_file=file,
        infinite=raw_tiled_map["infinite"],
        layers=[parse_layer(layer_, parent_dir) for layer_ in raw_tiled_map["layers"]],
        map_size=Size(raw_tiled_map["width"], raw_tiled_map["height"]),
        next_layer_id=raw_tiled_map["nextlayerid"],
        next_object_id=raw_tiled_map["nextobjectid"],
        orientation=raw_tiled_map["orientation"],
        render_order=raw_tiled_map["renderorder"],
        tiled_version=raw_tiled_map["tiledversion"],
        tile_size=Size(raw_tiled_map["tilewidth"], raw_tiled_map["tileheight"]),
        tilesets=tilesets,
        version=version,
    )

    layers = [layer for layer in map_.layers if hasattr(layer, "tiled_objects")]

    for my_layer in layers:
        # Mypy extremely hates what is going on in this whole block
        # For some reason an ignore on this first for loop is causing it
        # to just not care about any of the problems in here.
        # However, under normal circumstances, mypy hates just about every
        # line of this block.
        #
        # This is because we are doing some run-time modification of the attributes
        # on the tiled_object class and making assumptions about things based on that.
        # This is done to achieve a system where we can load-in tilesets which were
        # defined in a Tiled Object Template. This is tough because we need to know what
        # tilesets have been loaded in already, and use them if they have been, but then
        # be able to dynamically add-in tilesets after having parsed the rest of the map.

        for tiled_object in my_layer.tiled_objects:  # type: ignore
            if hasattr(tiled_object, "new_tileset"):
                if tiled_object.new_tileset is not None:
                    already_loaded = None
                    for val in map_.tilesets.values():
                        if val.name == tiled_object.new_tileset["name"]:
                            already_loaded = val
                            break

                    if not already_loaded:
                        highest_firstgid = max(map_.tilesets.keys())
                        last_tileset_count = map_.tilesets[highest_firstgid].tile_count
                        new_firstgid = highest_firstgid + last_tileset_count
                        map_.tilesets[new_firstgid] = parse_json_tileset(
                            tiled_object.new_tileset,
                            new_firstgid,
                            tiled_object.new_tileset_path,
                        )
                        tiled_object.gid = tiled_object.gid + (new_firstgid - 1)

                    else:
                        tiled_object.gid = tiled_object.gid + (
                            already_loaded.firstgid - 1
                        )

                    tiled_object.new_tileset = None
                    tiled_object.new_tileset_path = None

    if raw_tiled_map.get("class") is not None:
        map_.class_ = raw_tiled_map["class"]

    if raw_tiled_map.get("backgroundcolor") is not None:
        map_.background_color = parse_color(raw_tiled_map["backgroundcolor"])

    if raw_tiled_map.get("hexsidelength") is not None:
        map_.hex_side_length = raw_tiled_map["hexsidelength"]

    if raw_tiled_map.get("properties") is not None:
        map_.properties = parse_properties(raw_tiled_map["properties"])

    if raw_tiled_map.get("staggeraxis") is not None:
        map_.stagger_axis = raw_tiled_map["staggeraxis"]

    if raw_tiled_map.get("staggerindex") is not None:
        map_.stagger_index = raw_tiled_map["staggerindex"]

    _parallax_origin_x = 0
    _parallax_origin_y = 0

    if raw_tiled_map.get("parallaxoriginx") is not None:
        _parallax_origin_x = raw_tiled_map["parallaxoriginx"]

    if raw_tiled_map.get("parallaxoriginy") is not None:
        _parallax_origin_y = raw_tiled_map["parallaxoriginy"]

    map_.parallax_origin = OrderedPair(_parallax_origin_x, _parallax_origin_y)

    return map_
