

class EventReadyCls:
    ref_mediator = None

    def __init__(self):
        super().__init__()
        self._mediator = self.__class__.ref_mediator
        assert self._mediator is not None

    def pev(self, event_type, event=None, enable_event_forwarding=True):
        self._mediator.post(event_type, event, enable_event_forwarding)
