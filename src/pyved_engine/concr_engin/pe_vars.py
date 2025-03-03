"""
Public variables tied to the game engine.

WARNING: Although these variables can be accesed directly, it is NOT recommended
to tweak these values manually.
Unexpected outcomes/side-effects could be produced by doing so.
Instead use functions like pyv.preload_assets(...) or init(max_fps=..., ...) etc.

code by moonbak
contact - thomas.iw@kata.games

That file contains everything that's needed to implement
kengi.event... That is:

  - to_camelcase, and to_snakecase
  - (classes) EnumSeed, PseudoEnum, Singleton
  - EngineEvTypes (the enum)
"""
import re


# DECLARE CONSTANTS
# in regard to display options, within KENGI there are only 4 canonical modes for display:
#  three that are displayed in a 960 x 720 -pixel canvas
# 'super_retro' (upscaling x3), 'old_school', (upscaling x2), 'hd' (no upscaling)
# one that is displayed in a user-defined size canvas and also uses a pixel-to-pixel mapping just like the 'hd' option
# from pyved_engine.custom_struct import Objectifier

STD_SCR_SIZE = (960, 720)

# USEREVENT = 32850  # pygame userevent 2.1.1
# FIRST_ENGIN_TYPE = USEREVENT + 1
# FIRST_CUSTO_TYPE = FIRST_ENGIN_TYPE + 20  # therefore, 20 is the maximal amount of engine events


def to_camelcase(str_with_underscore):
    words = [word.capitalize() for word in str_with_underscore.split('_')]
    return "".join(words)


def to_snakecase(gname):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', gname)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class _CustomIter:
    """
    to make PseudoEnum instances -iterable-
    """

    def __init__(self, ref_penum):
        self._ref = ref_penum
        self._curr_idx = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._curr_idx >= self._ref.size:
            raise StopIteration
        else:
            idx = self._ref.order[self._curr_idx]
            self._curr_idx += 1
            return self._ref.content[idx]


def _enum_seed_implem(gt, c0):
    return {i: ename for (i, ename) in zip(gt, range(c0, c0 + len(gt)))}


# set an alias to define a "fake" class
EnumSeed = _enum_seed_implem


class PseudoEnum:
    def __init__(self, given_str_iterable, enumcode0=0):
        self._order = tuple(given_str_iterable)
        self._size = len(self._order)

        self._first = enumcode0
        self.content = EnumSeed(given_str_iterable, enumcode0)  # name to code

        self.inv_map = {v: k for k, v in self.content.items()}  # code to name

        tmp_omega = list()
        tmp_names_pep8f = list()
        for k in self._order:
            tmp_omega.append(self.content[k])
            tmp_names_pep8f.append(to_snakecase(k))
        self.omega = tuple(tmp_omega)
        self._names_pep8f = tuple(tmp_names_pep8f)

    def __getattr__(self, name):
        if name in self.content:
            return self.content[name]
        raise AttributeError("object has no attribute '{}'".format(name))

    @property
    def underscored_names(self):
        return self._names_pep8f

    @property
    def first(self):
        return self._first

    @property
    def order(self):
        return self._order

    @property
    def size(self):
        return self._size

    def __iter__(self):
        return _CustomIter(self)


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons. This should be used
    as a decorator -not a metaclass- to the class that should be a singleton.
    The decorated class can define one `__init__` function that takes only the `self`
    argument. Also, the decorated class cannot be inherited from.
    Other than that, there are no restrictions that apply to the decorated class.
    To get the singleton instance, use the `instance` method.
    Trying to use `__call__` will result in a `TypeError` being raised.
    """

    def __init__(self, decorated):
        self._decorated = decorated
        self._instance = None

    def instance(self):
        if self._instance is None:
            self._instance = self._decorated()
        return self._instance

    def __call__(self):
        err_msg = 'Singletons must be accessed through `instance()`'
        raise TypeError(err_msg)

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


# --- declare all engine events ---
_TRADITIONAL_1ST_ETYPE = 32866+1  # 32866 == pygame.USEREVENT


EngineEvTypes = PseudoEnum((
    'Quit',
    'Activation',
    'FocusGained',
    'FocusLost',
    'BasicTextinput',

    'Keydown',
    'Keyup',
    'Mousemotion',
    'Mousedown',
    'Mouseup',

    'Stickmotion',  # has event.axis; event.value
    'GamepadDir',
    'Gamepaddown',
    'Gamepadup',

    'Update',
    'Paint',

    'Gamestart',
    'Gameover',
    # (used in RPGs like niobepolis, conv<- conversation)
    'ConvStart',  # contains convo_obj, portrait
    'ConvFinish',
    'ConvStep',  # contains value

    'StateChange',  # contains code state_ident
    'StatePush',  # contains code state_ident
    'StatePop',

    'RpcReceive',  # two-level reception (->tunelling if we use the json-rpc). Has num and raw_rpc_resp attributes
    'RpcError',  # contains: code, msg

    'NetwSend',  # [num] un N°identification & [msg] un string (Async network comms)
    'NetwReceive'  # [num] un N°identification & [msg] un string (Async network comms)
), _TRADITIONAL_1ST_ETYPE)


class KengiEv:
    def __init__(self, etype, **entries):
        self.type = etype
        self.fields = entries
        self.__dict__.update(entries)


# below is a read-only value,
# to retrieve this value from outside you can call pyv.get_version()
ENGINE_VERSION_STR = '25.3a1'

DATA_FT_SIZE = 16

# deprecated but mandatory for web ctx
# ------------------------------------
# STD_SCR_SIZE = [960, 720]

BASE_ENGINE_EVS = [
    'update', 'draw',
    'mousemotion', 'mouseup', 'mousedown',
    'keyup', 'keydown', 'gameover',
    'conv_begins', 'conv_step', 'conv_finish',  # conversations with npcs
]

ev_manager = engine_events = None

bundle_name = None  # set by launcher script

omega_events = list(BASE_ENGINE_EVS)

# - engine related
mediator = None
disp_size = [960, 720]

# engine = None  # to store a reference to the ngine itself. Useful when writing pyv submodules!


backend_name = ''  # type str, and the default value is '' but it could be modified from elsewhere
weblib_sig = None

clock = None  # at some point, this should store a ref on an Obj. typed pygame.time.Clock
max_fps = 45  # will be replaced by whatever is passed to pyv.init(...)
screen = None

# - game related (universal behavior)
# 4 vars in order to handle all game assets
# images = dict()
# fonts = dict()
# spritesheets = dict()
# sounds = dict()
# csvdata = dict()
# data = dict()  # for raw json, most of the time

# 4 vars to handle the game loop conveniently
gameover = False
beginfunc_ref = updatefunc_ref = endfunc_ref = None
