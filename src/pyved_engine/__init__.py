"""
+----------------------------------------------------+
| Pyv - a pythonic 2d Game Engine                    |
| Our motto ~ Never slow down the innovation         |
|                                                    |
| https://github.com/gaudiatech/pyved-engine         |
| an open-source project started by GAUDIA TECH INC. |
|                                                    |
| Main author is: Thomas I. EDER / moonbak           |
| (github.com/wkta) - Contact thomas@katagames.io    |
+----------------------------------------------------+
"""
# from . import _hub
from .EngineRouter import EngineRouter
# from .Singleton import Singleton
# from ._classes import *
# from .compo import gfx
# from .compo import vscreen  # deprecated
from .compo.GameTpl import GameTpl  # legacy cls
# from .foundation import legacy_evs  # we just copy the event system of pygame
from .abstraction.EvSystem import Emitter, EvListener, EngineEvTypes
from .concr_engin import pe_vars as defs


# TODO remove this when we can
# ive kept it for retro-compatibility with projects that target pyv v23.6a1
# such as demos/ecs_naif or the very early stage pyved ships-with-GUI editor
# from .utils._ecs_pattern import entity, component, System, SystemManager, EntityManager
# from . import evsys0


_stored_kbackend = None
defs.weblib_sig = _backend_name = ''  # deprec.


def set_webbackend_type(xval):
    global _backend_name
    vars.weblib_sig = _backend_name = xval
    vars.backend_name = 'web'
