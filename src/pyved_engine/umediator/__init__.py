"""
As of time of writing (March 2025),
 this submodule is super-experimental

The goal in the long-run is to:
- totally abstract away the transport layer for network comms/networking

- allow the mediator class (also used in pyv.actors)
 to automatically process all [client server architecture]-based
  comms, therefore hiding "overhead"/complexities from the game dev

Overheard meaning what? In the computing Context:
extra resources (like time or memory) needed to manage or execute a process beyond the core tasks
"""
from .UMediator import UMediator
from .helpers import EventReadyCls
from .netlayer_factory import *  # imports the specific .build(a1, a2) function. Also contains the Objectifier cls
