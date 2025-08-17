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
from .concr_engin import pe_vars

# you can activate the lines below
# from . import evsys0
# from .utils._ecs_pattern import entity, component, System, SystemManager, EntityManager

# ...In case you need a stronger retro-compatibility with projects targeting pyv v23.6a1
# such as:
# - demos/ecs_naif, or
# - ships-with-GUI editor


_stored_kbackend = None
_context_type = 'local'
_stored_ev_source_cls = None


def set_exec_context(context_type: str, binding=None, stored_cls=None):
    global _context_type, _stored_kbackend, _stored_ev_source_cls
    assert context_type in ('local', 'web')
    _context_type = context_type
    if 'web' == context_type:
        if binding is None:
            raise ValueError('the "binding" argument is missing, in case of a web ctx')
        if stored_cls is None:
            raise ValueError('missing ev_source_cls')
        _stored_kbackend = binding
        _stored_ev_source_cls = stored_cls


def set_engine_ref(x):
    pe_vars.router_singleton = x


def get_engine_router() -> EngineRouter:
    """
    :return: the unique instance of EngineRouter class
    """
    if pe_vars.router_singleton:
        return pe_vars.router_singleton
    from .EngineRouter import EngineRouter
    # if 'local' == _context_type:
    #     from .abstraction.PygameWrapper import PygameWrapper
    #     xcls = PygameWrapper
    # else:
    #     xcls = _stored_kbackend
    y = pe_vars.router_singleton = EngineRouter()
    return y
