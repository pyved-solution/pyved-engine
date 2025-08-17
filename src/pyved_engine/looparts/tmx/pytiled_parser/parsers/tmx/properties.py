import xml.etree.ElementTree as etree
from pathlib import Path
from ...properties import Properties, Property
from ...util import parse_color


def parse(raw_properties: etree.Element) -> Properties:

    final: Properties = {}
    value: Property

    for raw_property in raw_properties.findall("property"):

        type_ = raw_property.attrib.get("type")

        if "value" not in raw_property.attrib:
            continue

        value_ = raw_property.attrib["value"]

        if type_ == "file":
            value = Path(value_)
        elif type_ == "color":
            value = parse_color(value_)
        elif type_ == "int" or type_ == "float":
            value = float(value_)
        elif type_ == "bool":
            if value_ == "true":
                value = True
            else:
                value = False
        else:
            value = value_
        final[raw_property.attrib["name"]] = value

    return final
