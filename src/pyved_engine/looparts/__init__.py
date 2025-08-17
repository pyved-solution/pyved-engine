"""
"looparts" sands for LOOSE PARTS

All elements in this sub-module are imported only via Injector
(our dependency injection manager)

So, follow guidelines and never import directly.

Another rule: elements in this sub-module have the right to access the engine router,
to use basic chunks of code such as "events", or "custom_struct" and so on.
"""

# N.b need to import so setup.py can detect all files
# from . import console
# from . import rogue
# from . import tabletop
# from . import terrain
