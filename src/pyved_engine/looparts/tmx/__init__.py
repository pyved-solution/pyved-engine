"""
TMX loading capabilities...

joint work:
- Richard Jones <richard@mechanicalcat.net>,
- Renfred Harper
- wkta-tom <thomas@gaudia-tech.com>
"""

from . import misc
from . import data
from . import pytiled_parser


_cached_ztm = None

def get_ztilemap_module():
    global _cached_ztm
    if not _cached_ztm:
        from . import ztilemap as _extra_module
        _cached_ztm = _extra_module
    return _cached_ztm
