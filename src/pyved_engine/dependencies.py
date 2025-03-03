import importlib
import inspect
from types import ModuleType
from typing import Any, Union, Callable, Dict


class LazyModule:
    """
    Lazy-loading via un proxy de module

    In our case:
     So, why is achieving a proper Lazy-loading so important?
    extension pyved modules require using low-level functions that rely on the Sublayer,
    but this implies the engine has to be already up and running.

    It would be difficult to implement extension pyved modules, if these are loaded instantly,
    not ensuring that the Sublayer etc. are ready...
    """
    def __init__(self, module_path: str, package: str = None):
        self.module_path = module_path
        self.package = package
        self._module = None  # ModuleType

    def proc_load(self) -> ModuleType:
        if self._module is None:
            print(f"Chargement paresseux du module : {self.module_path}")
            self._module = importlib.import_module(self.module_path, self.package)
        return self._module

    def __getattr__(self, name: str) -> Any:
        mod = self.proc_load()
        return getattr(mod, name)


class DependencyContainer:
    """
    A special container that helps a lot with
    dependency injection (injection de dépendances)
    """
    def __init__(self):
        self._dependencies: Dict[str, Any] = {}

    def register(self, key: str, dependency: Union[Any, LazyModule], interface: type = None) -> None:
        if interface is not None:
            # Pour un LazyModule, on charge le module temporairement pour la vérification.
            dep_instance = dependency
            if isinstance(dependency, LazyModule):
                dep_instance = dependency.proc_load()
            for attr in dir(interface):
                if callable(getattr(interface, attr, None)) and not attr.startswith("__"):
                    if not hasattr(dep_instance, attr):
                        raise ValueError(
                            f"La dépendance '{key}' n'implémente pas la méthode requise '{attr}' "
                            f"de l'interface {interface.__name__}."
                        )
        self._dependencies[key] = dependency

    def resolve(self, key: str) -> Any:
        if key not in self._dependencies:
            raise KeyError(f"Dépendance '{key}' non enregistrée.")
        return self._dependencies[key]

    def inject(self, func: Callable) -> Callable:
        sig = inspect.signature(func)

        def wrapper(*args, **kwargs):
            for param in sig.parameters:
                if param not in kwargs and param in self._dependencies:
                    kwargs[param] = self.resolve(param)
            return func(*args, **kwargs)
        return wrapper
