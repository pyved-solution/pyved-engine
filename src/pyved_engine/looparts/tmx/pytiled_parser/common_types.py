"""Module containing types that are common to other modules."""

# pylint: disable=too-few-public-methods

from typing import NamedTuple


class Color(NamedTuple):
    """Represents an RGBA color value as a four value Tuple.

    Attributes:
        red: Red value, between 0 and 255.
        green: Green value, between 0 and 255.
        blue: Blue value, between 0 and 255.
        alpha: Alpha value, between 0 and 255.
    """

    red: int
    green: int
    blue: int
    alpha: int


class Size(NamedTuple):
    """Represents a two dimensional size as a two value Tuple.

    Attributes:
        width: The width of the object. Can be in either pixels or number of tiles.
        height: The height of the object. Can be in either pixels or number of tiles.
    """

    width: float
    height: float


class OrderedPair(NamedTuple):
    """Represents a two dimensional position as a two value Tuple.

    Attributes:
        x: X coordinate. Can be in either pixels or number of tiles.
        y: Y coordinate. Can be in either pixels or number of tiles.
    """

    x: float
    y: float
