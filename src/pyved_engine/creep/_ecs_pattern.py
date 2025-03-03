"""
ECS - Entity Component system
heavily inspired by other projects authored by:
 - Vladimir Kaukin [KaukinVK@ya.ru]
 - Rik Cross [rik@raspberrypi.org]
"""
import collections
# from typing import Iterable, Iterator, Any
import dataclasses
import functools


# any entity class must be decorated with this function
entity = functools.partial(dataclasses.dataclass, slots=True)

# any component class must be decorated with this function
component = dataclasses.dataclass


class EntityManager:
    """Entity manager"""

    def __init__(self):
        self._entity_map = {}  # Person: [ent1, ent2]
        self._entity_components_map = {}  # Person: (MoveCom, DamageCom, NameCom)
        self._set_cache_map = {}  # (MoveCom, DamageCom, NameCom): {MoveCom, DamageCom, NameCom}
        self._delete_entity_buffer = collections.deque()  # deque([Person1, Person2])

    def add(self, *entity_value_list):
        """Add entities to world"""
        for entity_value in entity_value_list:
            assert getattr(entity_value, '__dict__', None) in (None, {}), 'Data class with inefficient memory usage'
            entity_value_class = entity_value.__class__
            self._entity_map.setdefault(entity_value_class, []).append(entity_value)
            if entity_value_class not in self._entity_components_map:
                self._entity_components_map[entity_value_class] = tuple(sorted(
                    (i for i in entity_value_class.__mro__ if i is not object),
                    key=lambda x: x.__class__.__name__
                ))

    def delete(self, *entity_value_list):
        """Delete entities from world"""
        for entity_value in entity_value_list:
            self._entity_map[entity_value.__class__].remove(entity_value)

    def delete_buffer_add(self, *entity_value_list):
        """Save entities into delete buffer for delete them from world later"""
        for entity_value in entity_value_list:
            self._delete_entity_buffer.append(entity_value)

    def delete_buffer_purge(self):
        """Delete all entities from delete buffer"""
        for delete_entity in self._delete_entity_buffer:
            self.delete(delete_entity)
        self._delete_entity_buffer.clear()

    def init(self, *entity_list):
        """
        Let entity manager to "know" about entities before work
        If manager do not know about entity, it will raise KeyError on access to it.
        event: SomeEvent = next(self.entities.get_by_class(SomeEvent), None)
        """
        for ent in entity_list:
            self.add(ent)
            self.delete(ent)

    def get_by_class(self, *entity_class_val_list: type):
        """
        Get all entities by specified entity class in specified order
        raise KeyError for uninitialized (never added) entities
        type returned is
        -> Iterator[Any]
        """
        for entity_class_val in entity_class_val_list:
            yield from self._entity_map[entity_class_val]

    def get_with_component(self, *component_class_val_list: type):
        """
        Get all entities that contains all specified component classes
        Sometimes it will be useful to warm up the cache
        raise KeyError for uninitialized (never added) entities
        type returned is
        -> Iterator[Any]
        """
        for entity_class, entity_component_list in self._entity_components_map.items():
            entity_component_set = \
                self._set_cache_map.setdefault(entity_component_list, set(entity_component_list))
            component_class_val_set = \
                self._set_cache_map.setdefault(component_class_val_list, set(component_class_val_list))
            if component_class_val_set.issubset(entity_component_set):
                yield from self._entity_map[entity_class]


class System:
    """
    Abstract base class for system
    All systems must be derived from this class
    System should have data for work: implement __init__ method
    """

    def initialize(self):
        """
        Preparing system to work before starting SystemManager.systems_update loop
        Runs by SystemManager.start_systems
        """

    def proc(self):
        """
        Run main system logic
        Runs by SystemManager.update_systems
        """

    def cleanup(self):
        """
        Clean system resources after stop update loop
        Runs by SystemManager.stop_systems
        """


class SystemManager:
    """
    System manager
    """

    def __init__(self):
        """
        :param system_list: an ordered sequence with systems, expected type is Iterable[System]
        such that
        for each pair of elements elt_i, elt_j we have classname(elt_i) != classname(elt_j)
        """
        self._system_list = None
        self._name_to_sys = dict()

        self._system_with_start_list = None
        self._system_with_update_list = None
        self._system_with_stop_list = None

    def declare_systems(self, system_list):
        self._system_list = tuple(system_list)

        self._name_to_sys.clear()

        for e in self._system_list:
            cls_name = e.__class__.__name__
            if cls_name in self._name_to_sys:
                raise Exception('ERR: Duplicate name for system detected!', cls_name)
            self._name_to_sys[cls_name] = e

        self._system_with_start_list = tuple(e for e in self._system_list if hasattr(e, 'initialize'))
        self._system_with_update_list = tuple(e for e in self._system_list if hasattr(e, 'proc'))
        self._system_with_stop_list = tuple(e for e in self._system_list if hasattr(e, 'cleanup'))

    # get by system name
    def __getitem__(self, item):
        return self._name_to_sys[item]

    def init_all(self):
        """Start all systems"""
        for system in self._system_with_start_list:
            system.initialize()

    def proc_all(self):
        """Update all systems"""
        for system in self._system_with_update_list:
            system.proc()

    def cleanup_all(self):
        """Stop all systems"""
        for system in self._system_with_stop_list:
            system.cleanup()
