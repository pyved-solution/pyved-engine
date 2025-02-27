"""
Rule:
- a game cartridge relies solely on the engine. The _ref_engine
that a game launcher uses will be cloned and become readable from here

- elements that you find in .looparts rely either on the engine itself,
 or on the sublayer for their implementation
The current file gets imported by any "shard"/ element of .looparts
"""


_ref_sublayer = None
_engine = None
_hub = {}  # in order to register pyv submodules as they're lazy-loaded. This idea is useful because
# submodules MAY CREATE dependencies between them,
# and we do not want neither the engineDev nor the gameDev to think about the order that works well
# when loading/importing submodules

# Whenever he/she is writing a new pyv submodule, the dev has to feel free


def set_sublayer(x):
    global _ref_sublayer
    if _ref_sublayer:
        raise RuntimeError('should no set _ref_sublayer more than once!')
    _ref_sublayer = x


def get_sublayer():
    return _ref_sublayer


def save_engine_ref(x):
    global _engine
    _engine = x  # storing a reference to the ngine itself. Useful when writing pyv submodules!


def ref_engine():
    if _engine is None:
        raise RuntimeError('asking for ref engine while the ref hasnt been saved yet!')
    return _engine

import re
from pathlib import Path


FONT = 'consolas'


def _font(size):
    return get_sublayer().SysFont(FONT, size)


def camel_case_format(string_ac_underscores):
    words = [word.capitalize() for word in string_ac_underscores.split('_')]
    return "".join(words)


def drawtext(msg, size=50, color=(255, 255, 255), aliased=False):
    return _font(size).render(msg, aliased, color)


def underscore_format(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def path_to_img_infos(filepath):
    """
    :param filepath: for example /users/tom/machin.png
    :return: both the future image name(identifier) that is "machin" and a filename thing to load: "machin.png"
    """
    pobj = Path(filepath)
    return pobj.stem, pobj.name
