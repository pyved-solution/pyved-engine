"""
replica of the pygame legacy event sys
"""
from . import dep_linking


def get():
    return dep_linking.pygame.event.get()


def pressed_keys():
    return dep_linking.pygame.key.get_pressed()


def __getattr__(name):  # expose(->like forwarding) all pygame key codes & pygame constants
    if name == 'QUIT':
        return dep_linking.pygame.QUIT
    try:
        return getattr(dep_linking.pygame.key, name)
    except AttributeError:
        return getattr(dep_linking.pygame, name)
