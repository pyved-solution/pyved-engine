from abc import ABC, abstractmethod


class NetwTransLayer(ABC):
    """
    Defining an interface (abstract class) for the network transport layer (high-level mechanism
    that forwards special events to REMOTE mediator objects
    """
    @abstractmethod
    def get_server_flag(self):
        pass

    @abstractmethod
    def start_comms(self, host_info, port_info):
        pass

    @abstractmethod
    def broadcast(self, ev_type, event_content):
        pass

    @abstractmethod
    def register_mediator(self, ref_mediator):
        pass

    @abstractmethod
    def shutdown_comms(self):
        pass
