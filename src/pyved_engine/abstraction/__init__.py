"""
in this module we should ALSO define standard transport layers for events that are "cross-events":
 - network layer based on sockets
 - network layer based on websockets
"""
from .PygameEvSource import PygameEvSource
from .PygameWrapper import PygameWrapper

# TODO
# deep_ev_source_cls = 'PygameEvSource'
# ws_transport_cls = 'WsTransportLocalCtx'

# then use importlib to load stuff.
# in that way, we'll be able to reconfigure at runtime!
# For example:

# deep_ev_source_cls = 'CanvasBasedEvSource'
# ws_transport_cls = 'WsTransportWebCtx'


def build_primalbackend(pbe_identifier, libbundle_ver=None):
    """
    :param pbe_identifier: str
    values accepted -> to make a valid func. call you would either pass '' or 'web'
    :param libbundle_ver: str
    """
    if pbe_identifier == '':  # default
        return PygameEvSource()

    elif pbe_identifier == 'web':
        if libbundle_ver is None:
            if vars.weblib_sig is None or len(vars.weblib_sig) < 1:
                raise ValueError('since you use the web backend you HAVE TO specify libbundle_ver !!')
            else:
                adhoc_ver = vars.weblib_sig
        else:
            adhoc_ver = libbundle_ver

        # its assumed that (injector entry 'web_pbackend')
        # => (module==web_pbackend.py & cls==WebPbackend)
        # for example
        modulename = 'web_pbackend'
        BackendAdhocClass = getattr(_hub.get_injector()[modulename], to_camelcase(modulename))
        print('   *inside build_primalbackend*  adhoc class is ', BackendAdhocClass)
        return BackendAdhocClass(adhoc_ver)  # web backends need to ver. info. in great details!
    else:
        raise ValueError(f'value "{pbe_identifier}" isnt supported, when calling (engine)build_primalbackend !')
