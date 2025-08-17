"""Property parsing for the JSON Map Format
"""

from pathlib import Path
from typing import List, Union, cast
# from typing_extensions import TypedDict
from ...properties import Properties, Property
from ...util import parse_color


# RawValue = Union[float, str, bool]

RawValue = float

# class RawProperty(TypedDict):
#     """The keys and their values that appear in a Tiled JSON Property Object.
#
#     Tiled Docs: https://doc.mapeditor.org/en/stable/reference/json-map-format/#property
#     """
#     name: str
#     type: str
#     value: RawValue


def parse(raw_properties):  #: List[RawProperty]) -> Properties:
    """Parse a list of `RawProperty` objects into `Properties`.

    Args:
        raw_properties: The list of `RawProperty` objects to parse.

    Returns:
        Properties: The parsed `Property` objects.
    """

    final: Properties = {}
    value: Property

    for raw_property in raw_properties:
        if raw_property["type"] == "file":
            value = Path(cast(str, raw_property["value"]))
        elif raw_property["type"] == "color":
            value = parse_color(cast(str, raw_property["value"]))
        else:
            value = raw_property["value"]
        final[raw_property["name"]] = value

    return final
