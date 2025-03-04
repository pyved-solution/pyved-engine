"""
As of time of writing (March 2025),
 this submodule is super-experimental

The goal in the long-run is to:
- totally abstract away the transport layer for network comms/networking
- allow the mediator class (also used in pyv.actors)
 to handle the client-server architecture+communication,
 but without any "overhead" for the game dev

Overheard meaning? In the computing Context: extra resources (like time or memory) needed to manage or execute
a process beyond the core tasks
"""
from .UMediator import UMediator
from .netlayer_factory import *  # the build(a1, a2) function, and also the Objectifier cls
from .helpers import EventReadyCls
