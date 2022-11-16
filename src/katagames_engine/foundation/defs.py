"""
code (c) 2018-2022, by Thomas Iwaszko
contact - tom@kata.games

That file contains everything that's needed to implement
kengi.event... That is:

  - to_camelcase, and to_snakecase
  - (classes) CircularBuffer, EnumSeed, PseudoEnum, Singleton
  - EngineEvTypes (the enum)

"""
import re
from collections import deque


# DECLARE CONSTANTS
# in regard to display options, within KENGI there are only 4 canonical modes for display:
#  three that are displayed in a 960 x 720 -pixel canvas
# 'super_retro' (upscaling x3), 'old_school', (upscaling x2), 'hd' (no upscaling)
# one that is displayed in a user-defined size canvas and also uses a pixel-to-pixel mapping just like the 'hd' option

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


class CircularBuffer:

    def __init__(self, gmax_len=128):
        """
        Initialize the CircularBuffer with a gmax_len if given. Default size is 128
        """
        self.deque_obj = deque(maxlen=gmax_len)

    def __str__(self):
        """Return a formatted string representation of this CircularBuffer."""
        items = ['{!r}'.format(item) for item in self.deque_obj]
        return '[' + ', '.join(items) + ']'

    def get_size(self):
        return len(self.deque_obj)

    def is_empty(self):
        """Return True if the head of the CircularBuffer is equal to the tail,
        otherwise return False"""
        return len(self.deque_obj) == 0

    def is_full(self):
        """Return True if the tail of the CircularBuffer is one before the head,
        otherwise return False"""
        return len(self.deque_obj) == self.deque_obj.maxlen

    def enqueue(self, item):
        """Insert an item at the back of the CircularBuffer
        Runtime: O(1) Space: O(1)"""
        self.deque_obj.append(item)

    def dequeue(self):
        """Return the item at the front of the Circular Buffer and remove it
        Runtime: O(1) Space: O(1)"""
        return self.deque_obj.popleft()

    def front(self):
        """Return the item at the front of the CircularBuffer
        Runtime: O(1) Space: O(1)"""
        if len(self.deque_obj):
            return self.deque_obj[len(self.deque_obj) - 1]
        raise IndexError('circular buffer is currently empty!')


# set an alias to define a "fake" class
EnumSeed = _enum_seed_implem


class PseudoEnum:
    def __init__(self, given_str_iterable, enumcode0=0):
        self._order = tuple(given_str_iterable)
        self._size = len(self._order)

        self._first = enumcode0
        self.content = EnumSeed(given_str_iterable, enumcode0)  # name to code
        print(self.content)
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

    'NetwSend',  # [num] un N°identification & [msg] un string (Async network comms)
    'NetwReceive'  # [num] un N°identification & [msg] un string (Async network comms)
), _TRADITIONAL_1ST_ETYPE)


class KengiEv:
    def __init__(self, etype, **entries):
        self.__dict__.update(entries)
        self.type = etype


if __name__ == '__main__':
    cb = CircularBuffer(3)
    print(str(cb))
    print("Empty: {}".format(cb.is_empty()))
    print("Full: {}".format(cb.is_full()))
    print()

    cb.enqueue("one")
    cb.enqueue("two")
    cb.enqueue("three")
    cb.enqueue("four")
    print(str(cb))
    print("Empty: {}".format(cb.is_empty()))
    print("Full: {}".format(cb.is_full()))
    print()

    print(cb.dequeue())

    print('front?', cb.front())
    print(str(cb))
    print(cb.get_size())
    print("Empty: {}".format(cb.is_empty()))
    print("Full: {}".format(cb.is_full()))
    print()

    cb.enqueue("five")
    cb.enqueue("six")
    print(str(cb))
    print('front? ', cb.front())
    print(cb.get_size())
    print("Empty: {}".format(cb.is_empty()))
    print("Full: {}".format(cb.is_full()))
    print()

    print(cb.dequeue())
    print(cb.dequeue())
    print(cb.dequeue())
    print(str(cb))
    print(cb.get_size())
    print("Empty: {}".format(cb.is_empty()))
    print("Full: {}".format(cb.is_full()))
