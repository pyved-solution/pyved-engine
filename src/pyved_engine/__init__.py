"""
| A pythonic 2d Game Engine
| Our motto ~ Never slow down the innovation
| https://github.com/pyved-solution/pyved-engine
| an open-source project initiated by GAUDIA TECH INC.

Main contributor: Thomas I. EDER / moonbak
Contact: thomas@katagames.io
"""
from . import hub
from .EngineRouter import EngineRouter
from .abstraction.EvSystem import Emitter, EvListener, EngineEvTypes
from .compo.GameTpl import GameTpl  # legacy class
from .concr_engin import pe_vars as defs

# you can activate the lines below
# from . import evsys0
# from .utils._ecs_pattern import entity, component, System, SystemManager, EntityManager

# ...In case you need a stronger retro-compatibility with projects targeting pyv v23.6a1
# such as:
# - demos/ecs_naif, or
# - ships-with-GUI editor


_stored_kbackend = None
defs.weblib_sig = _backend_name = ''  # deprec.


def get_engine_router():
    from .EngineRouter import EngineRouter
    from .abstraction.PygameWrapper import PygameWrapper
    return EngineRouter(PygameWrapper())


def set_webbackend_type(xval):
    global _backend_name
    defs.weblib_sig = _backend_name = xval
    defs.backend_name = 'web'
