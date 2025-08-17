"""This module provides classes for all layer types

There is the base Layer class, which TileLayer, ObjectLayer, ImageLayer,
and LayerGroup all derive from. The base Layer class is never directly used,
and serves only as an abstract base for common elements between all types.

For more information about Layers, see [Tiled's Manual](https://doc.mapeditor.org/en/stable/manual/layers/)
"""

# pylint: disable=too-few-public-methods

from pathlib import Path
from typing import List, Optional, Union

# import attr
from .common_types import Color, OrderedPair, Size
from .properties import Properties
from .tiled_object import TiledObject


class Layer:
    """Base class that all layer types inherit from. Includes common attributes between
    the various types of layers. This class will never be returned directly by the parser.
    It will always return one of the full layer types.

    `TMX Reference <https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#layer>`_

    `JSON Reference <https://doc.mapeditor.org/en/stable/reference/json-map-format/#layer>`_

    Attributes:
        name: The name of the layer object.
        opacity: Decimal value between 0 and 1 to determine opacity. 1 is completely
            opaque, 0 is completely transparent. Defaults to 1.
        visible: If the layer is visible in the Tiled Editor. Defaults to True
        coordinates: Where layer content starts in tiles. Only used by infinite maps.
            Defaults to (0, 0).
        parallax_factor: Used to determine parallaxing speed of a layer. Defaults to (1, 1).
        offset: Rendering offset of the layer object in pixels. Defaults to (0, 0).
        id: Unique ID of the layer. Each layer that is added to a map gets a unique id.
            Even if a layer is deleted, no layer ever gets the same ID.
        size: Ordered pair of size of map in tiles.
        properties: Properties for the layer.
        tint_color: Tint color that is multiplied with any graphics in this layer.
        class_: The Tiled class of this Layer.
        repeat_x: Repeat drawing on the X Axis(Currently only applies to image layers)
        repeat_y: Repeat drawing on the Y Axis(Currently only applies to image layers)
    """
    def __init__(self, name='', opacity=1, visible=True, repeat_x=False, repeat_y=False, coordinates=[0,0], id=0, parallax_factor=[1,1], size=[0,0]):
        self.name = name
        self.opacity = opacity
        self.visible = visible

        # These technically only apply to image layers as of now, however Tiled has indicated
        # that is only at this time, and there's no reason they couldn't apply to other
        # types of layers in the future. For this reason they are stored in the common class.
        self.repeat_x=repeat_x
        self.repeat_y = repeat_y

        self.coordinates = coordinates
        # TODO finish
        self.parallax_factor=parallax_factor
        # offset: OrderedPair = OrderedPair(0, 0)
        self.id = id
        # class_: Optional[str] = None
        self.size = size
        # properties: Optional[Properties] = None
        # tint_color: Optional[Color] = None


TileLayerGrid = List[List[int]]


class Chunk:
    """Chunk object for infinite maps. Stores `data` like you would have in a normal
    TileLayer but only for the area specified by `coordinates` and `size`.

    `Infinite Maps Docs <https://doc.mapeditor.org/en/stable/manual/using-infinite-maps/>`_

    `TMX Reference <https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#chunk>`_

    `JSON Reference <https://doc.mapeditor.org/en/stable/reference/json-map-format/#chunk>`_

    Attributes:
        coordinates: Location of chunk in tiles.
        size: The size of the chunk in tiles.
        data: The global tile IDs in the chunk. A row-first two dimensional array.
    """

    coordinates: OrderedPair
    size: Size
    data: List[List[int]]


# The tile data for one layer.
#
# Either a 2 dimensional array of integers representing the global tile IDs
#     for a TileLayerGrid, or a list of chunks for an infinite map layer.
LayerData = Union[TileLayerGrid, List[Chunk]]


class TileLayer(Layer):
    """The base type of layer which stores tile data for an area of a map.

    `Tiled Docs <https://doc.mapeditor.org/en/stable/manual/layers/#tile-layers>`_

    `TMX Reference <https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#layer>`_

    `JSON Reference <https://doc.mapeditor.org/en/stable/reference/json-map-format/#tile-layer-example>`_

    Attributes:
        chunks: List of chunks (only populated for infinite maps)
        data: A two dimensional array of integers representing the global
        tile IDs for the layer (only populaed for non-infinite maps)
    """

    chunks: Optional[List[Chunk]] = None
    data: Optional[List[List[int]]] = None


class ObjectLayer(Layer):
    """A Layer type which stores a list of Tiled Objects

    `Tiled Docs <https://doc.mapeditor.org/en/stable/manual/layers/#object-layers>`_

    `TMX Reference <https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#objectgroup>`_

    `JSON Reference <https://doc.mapeditor.org/en/stable/reference/json-map-format/#object-layer-example>`_

    Attributes:
        tiled_objects: List of tiled_objects in the layer.
        draworder: Whether the objects are drawn according to the order of the object
            elements in the object group element ('manual'), or sorted by their
            y-coordinate ('topdown'). Defaults to 'topdown'. See:
            https://doc.mapeditor.org/en/stable/manual/objects/#changing-stacking-order
            for more info.
    """
    def __init__(self,tiled_objects=None,draw_order='topdown', **kwargs):
        self.tiled_objects=list()
        if tiled_objects:
            self.tiled_objects=tiled_objects
        self.draw_order= draw_order
        super().__init__(**kwargs)


class ImageLayer(Layer):
    """A layer type which stores a single image

    `Tiled Docs <https://doc.mapeditor.org/en/stable/manual/layers/#image-layers>`_

    `TMX Reference <https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#imagelayer>`_

    `JSON Reference <https://doc.mapeditor.org/en/stable/reference/json-map-format/#layer>`_

    Attributes:
        image: The image used by this layer.
        transparent_color: Color that is to be made transparent on this layer.
    """

    image: Path
    transparent_color: Optional[Color] = None


class LayerGroup(Layer):
    """A layer that contains layers (potentially including other LayerGroups, nested infinitely).

    In Tiled, offset and opacity recursively affect child layers, however that is not enforced during
    parsing by pytiled_parser, and is up to the implementation how to handle recursive effects of
    LayerGroups

    `Tiled Docs <https://doc.mapeditor.org/en/stable/manual/layers/#group-layers>`_

    `TMX Reference <https://doc.mapeditor.org/en/stable/reference/tmx-map-format/#group>`_

    `JSON Reference <https://doc.mapeditor.org/en/stable/reference/json-map-format/#layer>`_

    Attributes:
        layers: list of layers contained in the group.
    """

    layers: Optional[List[Layer]]
