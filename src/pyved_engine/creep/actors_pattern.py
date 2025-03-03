import re
import uuid
from enum import Enum

from ..barebone import Objectifier
from ..concr_engin import pe_vars


# -------------- actor-based gamedev API (experimental) -------------------------
_debug_flag = False

DEFAULT_SCENE = 'default'
worlds = {DEFAULT_SCENE: {"actors": {}}}
_active_world = DEFAULT_SCENE
t_last_tick = None


def set_debug_flag(v=True):
    global _debug_flag
    _debug_flag = v


def declare_evs(*ev_names):
    del pe_vars.omega_events[:]
    pe_vars.omega_events.extend(pe_vars.BASE_ENGINE_EVS)
    if len(ev_names):
        pe_vars.omega_events.extend(ev_names)


# event system 6
class EventType(Enum):
    LOCAL = "local"
    TO_SERVER = "to_server"
    BROADCAST = "broadcast"


class Mediator:
    def __init__(self, network_layer=None, is_server=False):
        self.listeners = {}  # Dictionary to store listeners for each event type
        self.event_queue = []  # List to store pending events
        self.network_layer = network_layer  # Network layer for server communication
        self.is_server = is_server  # Indicates if this mediator is a server instance
        self.previous_world = None

    def register(self, event_type, listener, actor_id):
        """Registers a listener (callback function) for a specific event type."""
        if event_type not in self.listeners:
            self.listeners[event_type] = {}
        self.listeners[event_type][actor_id] = listener

    def unregister(self, actor_id):
        """Unregisters all listeners for a specific actor."""
        for event_type in list(self.listeners.keys()):
            if actor_id in self.listeners[event_type]:
                del self.listeners[event_type][actor_id]
            if not self.listeners[event_type]:
                del self.listeners[event_type]

    def post(self, event_type, event, cross_type):
        """Posts an event to the event queue, with cross-event type (local, to_server, broadcast)."""
        if not self.network_layer or not cross_type:
            self.event_queue.append((event_type, Objectifier(event)))  # handle locally
            return

        if not self.is_server:
            # Send the event to the server
            # ??? self.network_layer.send_event(event_type, event)
            self.network_layer.broadcast(event_type, event)
        else:
            # Broadcast to all clients (assuming we have a list of client mediators)
            for client in self.network_layer.get_connected_clients():
                client.post(event_type, event)

    def update(self):
        """Processes the event queue by notifying listeners for each event."""
        cpt = len(self.event_queue)
        while cpt > 0:
            event_type, event = self.event_queue.pop(0)  # Get the next event, the FIFO way
            cpt -= 1
            if event_type not in self.listeners:
                continue

            mapping = self.listeners[event_type].copy()
            for to_whom, callback in mapping.items():
                if to_whom not in worlds[_active_world]['actors']:
                    continue  # world has changed
                adhoc_data = worlds[_active_world]['actors'][to_whom]['data']
                callback(adhoc_data, event)

        if self.previous_world is not None:
            # unregister actors of the current world
            for actor_id in worlds[self.previous_world]["actors"].keys():
                self.unregister(actor_id)
            self.previous_world = None

    # ---------- networking ----------------
    def set_network_layer(self, ref):
        if self.network_layer is not None:
            raise RuntimeError('cannot bind another network layer, one has already be set')
        self.network_layer = ref
        ref.register_mediator(self)


def ls_scenes():
    """Lists all existing scenes."""
    return list(worlds.keys())


def get_scene():
    return _active_world


def set_scene(newworld_name):
    """
    switches to the specified world context. Creates it if it doesn't exist
    """
    global _active_world
    # we do this, to allow the mediator to unregister all actors from previous world, when appropriate
    pe_vars.mediator.previous_world = _active_world

    # Creating a new world if it doesnt exist
    if newworld_name not in worlds:
        worlds[newworld_name] = {
            "actors": {}
        }
    # switch to the world "newworld_name"
    _active_world = newworld_name
    if _debug_flag:
        print('new world:', newworld_name)

    # Let's register back all actors that do exist in this world
    for actor_id, actor_data in worlds[_active_world]["actors"].items():
        if _debug_flag:
            print(f're-bind all event handlers for actor {actor_id}')
        # Re-register the actor's event handlers
        for event_type, handler in actor_data["event_handlers"].items():
            pe_vars.mediator.register(event_type, handler, actor_id)


def delete_world(name):
    """Deletes the specified world context if it is not the currently active one."""
    global _active_world
    if name != _active_world and name in worlds:
        del worlds[name]


def new_actor(actor_type, local_scope):
    """
    Automatically gathers functions in the local scope that follow the `on_X` naming convention
    (where X can be any combination of letters or underscores), and creates an event_handlers
    dictionary mapping the event types to the functions.

    When calling the function,
    need to provide the local scope via "locals()"
    """
    # Define a regex pattern to match function names starting with 'on_'
    pattern = re.compile(r"on_[A-Za-z_]+")

    # upgrade the data from actor
    packed_data = packing_data(local_scope['data'])

    # setattr(packed_data, 'functions',
    tempfunc = {
        func_name: func
        for func_name, func in local_scope.items()
        if callable(func) and not pattern.match(func_name)
    }

    # Create the event_handlers dictionary by filtering functions that match the pattern
    event_handlers = {
        func_name.replace("on_", ""): func
        for func_name, func in local_scope.items()
        if callable(func) and pattern.match(func_name)
    }
    for fname_key in event_handlers:
        if fname_key not in pe_vars.omega_events:
            print('__ Have you called pyv.setup_evsys6 with the right parameters? __')
            raise ValueError(f'unfinished actor {actor_type} tries to bind func to INVALID ev_type:{fname_key}')

    # Create a unique identifier for the actor
    actor_id = str(uuid.uuid4())
    actor_data = {
        "name": actor_type,
        "data": packed_data,
        "event_handlers": event_handlers,
        "functions": tempfunc
    }
    worlds[_active_world]["actors"][actor_id] = actor_data

    # Register the event handlers
    # TODO need fix?
    for event, handler in event_handlers.items():
        pe_vars.mediator.register(f"{event}", handler, actor_id)
    # print('creation actor: ', actor_id)
    return actor_id


def id_actor(ptr_data):
    """
    reverse: given data, provide the actor_id
    """
    for uid, actor_record in worlds[_active_world]["actors"].items():
        if id(actor_record['data']) == id(ptr_data):
            return uid
    raise IndexError('cant find actor specified, provided data:', ptr_data)


def del_actor(*args):
    """Unregisters all event handlers and removes the actor from the current world."""
    for actor_id in args:
        if actor_id is None:
            raise ValueError('tried to del_actor, but passed value:None')

        if actor_id in worlds[_active_world]["actors"]:
            del worlds[_active_world]["actors"][actor_id]
        pe_vars.mediator.unregister(actor_id)
        # print('deletion actor: ', actor_id)


def peek(actor_id):
    """Returns the state of the actor with the given ID in the current world."""
    if actor_id is None:
        raise ValueError('passing an actor_id, with value:None')
    if actor_id not in worlds[_active_world]["actors"]:
        print(f'***Warning! Trying to access actor {actor_id}, not found in the current world')
        return None
    return worlds[_active_world]["actors"].get(actor_id)["data"]


def trigger(func_name, actor_id, *extra_args):
    actor_name = worlds[_active_world]["actors"].get(actor_id)["name"]

    # func_table = actor_state_res.functions
    func_table = worlds[_active_world]["actors"].get(actor_id)["functions"]
    # the effective call
    if func_name not in func_table:
        raise SyntaxError(f'cannot find function "{func_name}" for actor "{actor_name}" id:{actor_id}')
    else:
        this_arg = worlds[_active_world]["actors"].get(actor_id)["data"]
        return func_table[func_name](this_arg, *extra_args)


def packing_data(given_data):
    return Objectifier(given_data)
