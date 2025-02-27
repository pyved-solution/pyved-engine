# import importlib.util
from abc import ABCMeta, abstractmethod
from collections import deque


__all__ = [
    'BaseGameState',
    'Objectifier',
    'CircularBuffer'
]


class BaseGameState(metaclass=ABCMeta):

    def __init__(self, state_ident):
        self.__state_ident = state_ident
        self.__state_name = self.__class__.__name__

    @abstractmethod
    def enter(self):
        pass

    def get_id(self):
        return self.__state_ident

    def get_name(self):
        return self.__state_name

    def pause(self):
        print(self.__class__.__name__)
        raise AssertionError('not meant to be paused')

    @abstractmethod
    def release(self):
        pass

    def resume(self):
        print(self.__class__.__name__)
        raise AssertionError('not meant to be resumed')


# may be deprecated, due to pyv.vars
# TODO investigate?
# class ConfigStorage:
#     MAXFPS = 45
#     SCR_SIZE = (None, None)
#     UPSCALING = None  # not defined, yet


class Objectifier:
    def __init__(self, **entries):
        self.__dict__.update(entries)


# ---------------------------------
#  historically this was in "hub"
# ---------------------------------
class PyModulePromise:
    verbose = 1
    JIT_MSG_LOADING = '*Pyv add-on "{}" is ready! Loading on-the-fly ok*'
    ref_to_pygame = None

    def __init__(self, mod_name: str, pypath: str, pck_arg: str):
        self._ref_module = None
        self._module_name = mod_name
        self._py_path = pypath
        self.pck_arg = pck_arg

    def is_ready(self):
        return self._ref_module is not None

    @property
    def name(self):
        return self._module_name

    @property
    def result(self):
        if not self.is_ready():
            self._jit_load_module_op(self.pck_arg)
        return self._ref_module

    def _jit_load_module_op(self, pck_arg):
        cls = self.__class__
        if cls.verbose:  # and nam != 'pygame':  # print a debug info.
            print(cls.JIT_MSG_LOADING.format(self.name))

        # Check if the path starts with 'pygame' and strip it for modular navigation
        string = self._py_path
        if string.split('.')[0] == 'pygame':
            # Split the path and discard the 'pygame' part, keeping only the rest
            path_parts = string.split('.')[1:]
            # Start with the base pygame reference
            ref = self.__class__.ref_to_pygame
            # Iterate through each part to navigate to the target attribute
            for part in path_parts:
                print(' getattr called with args::', ref, part)
                ref = getattr(ref, part)
            self._ref_module = ref
            return
        if (pck_arg is not None) and self._py_path[0] == '.':
            self._ref_module = importlib.import_module(self._py_path, pck_arg)
        else:
            self._ref_module = importlib.import_module(self._py_path)


class Injector:
    """
    gere chargement composants engine + any engine plugin
    Le fait au moyen dun tableau:
    module name <-> instance of LazyModule
    """

    def __init__(self, module_listing, package_arg):
        self._listing = dict()
        for mname, pypath in module_listing.items():
            obj = PyModulePromise(mname, pypath, package_arg)
            self._listing[obj.name] = obj
        self._man_set = dict()
        self._loading_done = False

    def hack_package_arg(self, new_val):  # useful for the katasdk
        for prom_obj in self._listing.values():
            prom_obj.pck_arg = new_val

    def __contains__(self, item):
        if item in self._man_set:
            return True
        else:
            return item in self._listing

    def set(self, mname, pymod):
        if mname == 'pygame':
            PyModulePromise.ref_to_pygame = pymod  # auto- bind
            print('auto bind')
        self._man_set[mname] = pymod

    def __getitem__(self, item):
        if item in self._man_set:
            return self._man_set[item]
        else:
            res = self._listing[item].result
            self._loading_done = True
            return res

    def is_loaded(self, pckname):
        return self._listing[pckname].is_ready()

    def register(self, sm_name, py_path, pck_arg):
        if self._loading_done:
            print('***warning*** register plugin should be done before using loading elements')
        self._listing[sm_name] = PyModulePromise(sm_name, py_path, pck_arg)
