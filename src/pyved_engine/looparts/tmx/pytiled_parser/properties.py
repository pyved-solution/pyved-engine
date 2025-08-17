"""Properties Module

This module defines types for Property objects.
For more about properties in Tiled maps see the below link:
https://doc.mapeditor.org/en/stable/manual/custom-properties/

The types defined in this module get added to other objects
such as Layers, Maps, Objects, etc
"""

from pathlib import Path
from typing import Dict, Union

from .common_types import Color

Property = Union[float, Path, str, bool, Color]

Properties = Dict[str, Property]
