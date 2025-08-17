"""
(~*~ legacy code ~*~)
AUTHOR INFO
 Joseph H. cf. https://github.com/jwvhewitt

LICENSE INFO
 for the whole polarbear folder: Apache 2.0

Below are chunks extracted from the Polar Bear Game Engine.
This package contains some low-level graphics stuff needed to
create an isometric RPG style rules in Python. The idea is to
isolate the graphics handling from the code as much as possible,
so that if PyGame is replaced the interface shouldn't change
too much. Also, so that creating a new rules should be as simple
as importing this package.
Word wrapper taken from the PyGame wiki plus the list-printer
from Anne Archibald's GearHead Prime demo.
"""

from . import image
from . import widgets
from .general import default_border, render_text,  INFO_GREEN  # wait_event, TIMEREVENT
from .image import draw_text
