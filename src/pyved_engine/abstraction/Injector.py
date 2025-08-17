# -----------------
#  all this is deprecated in 2025
#  it was replaced by:
#    "dependencies.py"
#  fin
# -----------------
# The injector class is useful for two distinct pupose:
# - (1) performance, via the lazy-loading implementation. This is used in hub.py for engine modules
# that are not that commonly used
#
# - (2) advanced dependency injection. Imagine one needs to bring classes that aren't part of the
# PyvedEngine project but still follow the interface of the Abstract class properly.
# If one wishes to inject the "alien-like" class in the project, using an instance of Injector
# will be much much "cleaner"
import importlib


class PyModulePromise:
    """
    will be useful to load dynamicall some engine modules not often used,
    such as .isometric.
    Can save resources/CPU cycles when launching the game.
    """
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
        if cls.verbose:
            print(cls.JIT_MSG_LOADING.format(self.name))
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

    def __contains__(self, item):
        if item in self._man_set:
            return True
        else:
            return item in self._listing

    def set(self, mname, pymod):
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
