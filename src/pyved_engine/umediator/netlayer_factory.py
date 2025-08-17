"""
Class to provide high flexibility in network communications.

It allows for easy switching between different interfaces by constructing
the appropriate one on demand. This is achieved by passing two arguments:

- Context: Game with both client and server components
"""
import importlib


__all__ = [
    'build_netlayer',
    'build_netlayer_from_module',
    'Objectifier'
]


class Objectifier:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def build_netlayer_from_module(pymod):
    # Extract the functions
    f1 = getattr(pymod, 'get_server_flag')
    f2 = getattr(pymod, 'start_comms')
    f3 = getattr(pymod, 'broadcast')
    f4 = getattr(pymod, 'register_mediator')
    f5 = getattr(pymod, 'shutdown_comms')
    dict_repr_netlayer = {
        'get_server_flag': f1,
        'start_comms': f2,
        'broadcast': f3,
        'register_mediator': f4,
        'shutdown_comms': f5
    }
    return Objectifier(**dict_repr_netlayer)


def build_netlayer(param1, param2):
    """
    Helps retrieving functions from a particular netw_* module,
    based on the two given parameters.
    :param param1: info about the context/technology such as 'socket', 'ws', or 'nodejs'
    :param param2: either 'client' or 'server', nothing else
    :return: a dictionary of functions
    """
    print('internal PYV init step:<build_netlayer Func>, params:', param1, param2)

    # mapping of parameter pairs -to-> module names
    # Feel free to add more items, if needed
    netw_strat_table = {
        ('socket', 'client'): 'netw_socket_cli',
        ('socket', 'server'): 'netw_socket_server',
        ('ws', 'client'): 'netw_ws_client',
        ('ws', 'server'): 'netw_ws_serv',
    }

    # Import the ad-hoc module dynamically, then build a netlayer from it
    module_name = netw_strat_table.get((param1, param2))
    if not module_name:
        raise ValueError(f"No transport layer definition module suitable for params: {param1},{param2}")

    resulting_netlayer = build_netlayer_from_module(
        importlib.import_module('.netw_strategies.'+module_name, package='pyved_engine.umediator')
    )
    return resulting_netlayer
