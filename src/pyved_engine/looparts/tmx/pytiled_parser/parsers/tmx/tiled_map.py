import json
import xml.etree.ElementTree as etree
from pathlib import Path
from ...common_types import OrderedPair, Size
from ...exception import UnknownFormat
from ...parsers.json.tileset import parse as parse_json_tileset
from ...parsers.tmx.layer import parse as parse_layer
from ...parsers.tmx.properties import parse as parse_properties
from ...parsers.tmx.tileset import parse as parse_tmx_tileset
from ...tiled_map import TiledMap, TilesetDict
from ...util import check_format, parse_color


def parse(file: Path) -> TiledMap:
    """Parse the raw Tiled map into a pytiled_parser type.

    Args:
        file: Path to the map file.

    Returns:
        TiledMap: A parsed TiledMap.
    """
    with open(file) as map_file:
        raw_map = etree.parse(map_file).getroot()

    parent_dir = file.parent

    raw_tilesets = raw_map.findall("./tileset")
    tilesets: TilesetDict = {}

    for raw_tileset in raw_tilesets:
        if raw_tileset.attrib.get("source") is not None:
            # Is an external Tileset
            tileset_path = Path(parent_dir / raw_tileset.attrib["source"])
            parser = check_format(tileset_path)
            with open(tileset_path) as tileset_file:
                if parser == "tmx":
                    raw_tileset_external = etree.parse(tileset_file).getroot()
                    tilesets[int(raw_tileset.attrib["firstgid"])] = parse_tmx_tileset(
                        raw_tileset_external,
                        int(raw_tileset.attrib["firstgid"]),
                        external_path=tileset_path.parent,
                    )
                elif parser == "json":
                    tilesets[int(raw_tileset.attrib["firstgid"])] = parse_json_tileset(
                        json.load(tileset_file),
                        int(raw_tileset.attrib["firstgid"]),
                        external_path=tileset_path.parent,
                    )
                else:
                    raise UnknownFormat(
                        "Unkown Tileset format, please use either the TSX or JSON format."
                    )

        else:
            # Is an embedded Tileset
            tilesets[int(raw_tileset.attrib["firstgid"])] = parse_tmx_tileset(
                raw_tileset, int(raw_tileset.attrib["firstgid"])
            )

    layers = []
    for element in raw_map.iter():
        if element.tag in ["layer", "objectgroup", "imagelayer", "group"]:
            layers.append(parse_layer(element, parent_dir))

    map_ = TiledMap(
        map_file=file,
        infinite=bool(int(raw_map.attrib["infinite"])),
        layers=layers,
        map_size=Size(int(raw_map.attrib["width"]), int(raw_map.attrib["height"])),
        next_layer_id=int(raw_map.attrib["nextlayerid"]),
        next_object_id=int(raw_map.attrib["nextobjectid"]),
        orientation=raw_map.attrib["orientation"],
        render_order=raw_map.attrib["renderorder"],
        tiled_version=raw_map.attrib["tiledversion"],
        tile_size=Size(
            int(raw_map.attrib["tilewidth"]), int(raw_map.attrib["tileheight"])
        ),
        tilesets=tilesets,
        version=raw_map.attrib["version"],
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
                        if val.name == tiled_object.new_tileset.attrib["name"]:
                            already_loaded = val
                            break

                    if not already_loaded:
                        print("here")
                        highest_firstgid = max(map_.tilesets.keys())
                        last_tileset_count = map_.tilesets[highest_firstgid].tile_count
                        new_firstgid = highest_firstgid + last_tileset_count
                        map_.tilesets[new_firstgid] = parse_tmx_tileset(
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

    if raw_map.attrib.get("backgroundcolor") is not None:
        map_.background_color = parse_color(raw_map.attrib["backgroundcolor"])

    if raw_map.attrib.get("hexsidelength") is not None:
        map_.hex_side_length = int(raw_map.attrib["hexsidelength"])

    properties_element = raw_map.find("./properties")
    if properties_element:
        map_.properties = parse_properties(properties_element)

    if raw_map.attrib.get("staggeraxis") is not None:
        map_.stagger_axis = raw_map.attrib["staggeraxis"]

    if raw_map.attrib.get("staggerindex") is not None:
        map_.stagger_index = raw_map.attrib["staggerindex"]

    if raw_map.attrib.get("class") is not None:
        map_.class_ = raw_map.attrib["class"]

    _parallax_origin_x = 0.0
    _parallax_origin_y = 0.0

    if raw_map.attrib.get("parallaxoriginx") is not None:
        _parallax_origin_x = float(raw_map.attrib["parallaxoriginx"])

    if raw_map.get("parallaxoriginy") is not None:
        _parallax_origin_y = float(raw_map.attrib["parallaxoriginy"])

    map_.parallax_origin = OrderedPair(_parallax_origin_x, _parallax_origin_y)

    return map_
