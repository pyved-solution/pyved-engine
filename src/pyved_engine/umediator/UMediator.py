import random
from .helpers import EventReadyCls


# @Singleton
class UMediator:
    def __init__(self):
        self.ident = self.gen_id()
        self.listeners = {}
        self.event_queue = list()  # deque()
        self.network_layer = None

        EventReadyCls.ref_mediator = self

    def set_network_layer(self, ref):
        self.network_layer = ref
        ref.register_mediator(self)

    @staticmethod
    def gen_id():
        omega = [chr(c) for c in range(ord('a'), ord('z') + 1)] + [str(e) for e in range(0, 10)]
        lst = [random.choice(omega) for _ in range(12)]
        return "".join(lst)

    def register(self, event_type, listener):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)

    def unregister(self, event_type, listener):
        if event_type in self.listeners:
            self.listeners[event_type].remove(listener)
            if not self.listeners[event_type]:
                del self.listeners[event_type]

    @staticmethod
    def is_special_event(event_type):
        return event_type.startswith('x_')

    def _basic_notify(self, event_type, event):
        if event_type in self.listeners:
            for listener_cb in self.listeners[event_type]:
                listener_cb(event)

    def post(self, event_type, event: str, enable_event_forwarding: bool):
        if event_type not in ('paint', 'update'):
            print(f'  postage event [{event_type}, {event}] sur Mediator:', self.ident)
        self.event_queue.append((event_type, event, enable_event_forwarding))

    def _update_step(self):
        y = cpt = len(self.event_queue)

        while cpt > 0:
            event_type, event, enable_event_forwarding = self.event_queue.pop(0)  # .popleft()
            if event_type not in ('update', 'paint'):
                print('-unpop event from queue:', event_type)

            if self.is_special_event(event_type) and enable_event_forwarding:
                self.handle_special_event(event_type, event)
            else:
                if event_type not in ('update', 'paint'):
                    print('->basic notify')
                self._basic_notify(event_type, event)
            cpt -= 1
        return y

    def update(self, save_cycles=False):
        if save_cycles:
            self._update_step()
        else:
            t = self._update_step()
            while t != 0:
                t = self._update_step()

    def handle_special_event(self, event_type, event):
        suffix = " by server" if self.network_layer.get_server_flag() else "by client"+self.ident
        print(f"Special event [{event_type}, {event}] forwarded"+suffix)
        self.network_layer.broadcast(event_type, event)
