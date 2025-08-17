"""
ECS (Entity-Component-System) is an architectural pattern commonly used in game dev
to structure the organization and behavior of entities within a game. It provides
a flexible and scalable approach to handle complex game systems and interactions.
"""
# -------------
#  kept for retro-compatibility and not breaking
#  the platformer video tutorial
# -------------
_legacy_components = {}
_legacy_archetypes = {}
_legacy_entities = []
# _legacy_systems = []
# -------------
#  new storage
# -------------
_archetypes = dict()  # arche-name to <list of entity ids>
_archetype_def = dict()  # arche-name to <list of compo-names>
_components = dict()  # compo-name to <list of ids>
_free_id = -1 * 0x87aebf7
_curr_world = 'default'  # TODO structure scene by scene
_entities = list()
_systems = list()


# def new_entity():
#     entity = {}
#     _legacy_entities.append(entity)
#     return entity


# def delete_entity(entity):
#     _legacy_entities.remove(entity)

def init_entity(entity, values):
    entity.update(values)


def dissect_entity(given_ent, keys_li):
    return [given_ent[k] for k in keys_li]


# def new_from_archetype(archetype_name):
#     if archetype_name not in _legacy_archetypes:
#         raise KeyError(f"ERR: Archetype {archetype_name} is not valid!")
#     entity = new_entity()
#     for component_name in _legacy_archetypes[archetype_name]:
#         add_component(entity, component_name, None)
#     add_component(entity, 'Archetype', archetype_name, bypass=True)
#     return entity


# fix
def new_from_archetype(archetype_name):
    eo = new_entity()
    eo.set_archetype(archetype_name)
    return eo


# def define_archetype(archetype_name, component_names):
#     _legacy_archetypes[archetype_name] = component_names
#
def define_archetype(archetype_name, component_names):
    _archetype_def[archetype_name] = component_names
    _archetypes[archetype_name] = list()


# def has_archetype(entity, archetype_name):
#     if 'Archetype' not in entity:
#         return False
#     return entity['Archetype'] == archetype_name
#
#
# def find_by_archetype(archetype_name):
#     return list(filter(lambda e: has_archetype(e, archetype_name), _legacy_entities))
#
#
# def list_all_archetypes():
#     return tuple(_legacy_archetypes.keys())

def has_archetype(entity, archetype_name):
    return entity.archetype == archetype_name


def find_by_archetype(archetype_name):
    li_e_id = _archetypes[archetype_name]
    return list(map(lambda x: _EntityCls.globalmapping[x], li_e_id))


def list_all_archetypes():
    return tuple(_archetypes.keys())


def archetype_of(entity_ref):  # we simply extract the archetype
    return entity_ref.archetype


# def archetype_of(entity_ref):
#     if 'Archetype' not in entity_ref:
#         return None
#     return entity_ref['Archetype']


# --------------------------------
#  new API for using ecs
# --------------------------------
class _EntityCls:
    globalmapping = dict()

    def __init__(self, eid, li_components=None):
        self._id = eid
        self._archetype = None
        self.__class__.globalmapping[eid] = self
        self.icomponents = dict()
        self._compo_order = list()
        if li_components:
            for componame in li_components:
                self.add_component(componame)

    @property
    def id(self):
        return self._id

    @property
    def components(self):
        return list(self._compo_order)

    def has_component(self, componame):
        return self._id in _components[componame]

    @property
    def archetype(self):
        return self._archetype

    def set_archetype(self, a_name):
        if a_name not in _archetypes.keys():
            raise ValueError(f'Archetype {a_name} not declared')
        if self._archetype:
            raise NotImplementedError(f'Cannot set new archetype, entity is already archetype {self._archetype}')
        self._archetype = a_name
        _archetypes[a_name].append(self._id)
        if len(self.icomponents):
            print('* warning setting archetype to an entity that alreay has components ->wipe out existing data *')
        self.icomponents.clear()
        _exp_components = _archetype_def[a_name]
        for c in _exp_components:
            self.add_component(c)

    def add_component(self, key, val=None):
        if key in self.icomponents:
            raise ValueError(f'Compo {key} already exist on entity, cannot add again!')
        self.icomponents[key] = val
        self._compo_order.append(key)

        if key not in _components:
            _components[key] = list()
        _components[key].append(self._id)

    def remove_component(self, key):
        raise NotImplementedError

    def update(self, dico):
        for elt in dico.keys():
            if elt not in self.icomponents.keys():
                raise ValueError(f'Compo found in dictionary ({elt})does not exist in the entity')
        for k, v in dico.items():
            self.icomponents[k] = v

    def __getattr__(self, item):
        return self.icomponents[item]

    def __getitem__(self, k):  # forward to dict, unless its an int
        if isinstance(k, int):
            return self._compo_order[k]
        else:
            return self.icomponents.__getitem__(k)

    def __setitem__(self, key, value):
        self.icomponents[key] = value


# Entity functions -----
def new_entity(archetype=None, **kwargs):
    global _free_id
    e_id = _free_id
    _free_id += 1
    res = _EntityCls(e_id)
    if archetype:
        if archetype in _archetypes.keys():
            res.set_archetype(archetype)
            if len(kwargs) > 0:
                res.update(kwargs)
        else:
            raise ValueError(f'Specified archetype {archetype} is unknown!')
    _entities.append(res)
    return res


def delete_entity(entity):
    eid = entity.id
    if entity.archetype is not None:
        _archetypes[entity.archetype].remove(eid)
    for cname in entity.components:
        _components[cname].remove(eid)
    _entities.remove(entity)


# def wipe_entities():
#     del _legacy_entities[:]

def wipe_entities():
    for cn, li_entities in _components.items():
        del li_entities[:]
    for a, li_eid in _archetypes.items():
        del li_eid[:]


# def add_component(entity, component_name, data, bypass=False):
#     if not bypass and component_name == 'Archetype':
#         raise ValueError('ERR: Cannot declare a component named "Archetype"!')
#     component = {component_name: data}
#     entity.update(component)
#     if component_name not in _legacy_components:
#         _legacy_components[component_name] = []
#     _legacy_components[component_name].append(entity)

def add_component(entity, component_name, data, bypass=False):
    if not bypass and component_name == 'Archetype':
        raise ValueError('ERR: Cannot declare a component named "Archetype"!')
    entity.add_component(component_name, data)


# def remove_component(entity, component_name):
#     if component_name in entity:
#         entity.pop(component_name)
#         if component_name in _legacy_components:
#             _legacy_components[component_name].remove(entity)

def remove_component(entity, component_name):
    if component_name in entity:
        entity.pop(component_name)
        if component_name in _components:
            _components[component_name].remove(entity)


def find_by_components(*compokeys):
    """
    this func will return all entities that satisfy each on of compokeys (=has that list of components in it)
    :param compokeys:
    :return: a list
    """
    res = list()
    for entity in _entities:
        # print('curr entity:', entity)
        compat = True
        for c in compokeys:
            if not entity.has_component(c):
            # below line = faster, used to break things in web Ctx
            # if c not in entity: 
                compat = False
                break
        if compat:
            res.append(entity)
    return res


def all_entities(scene=None):
    return iter(_entities)  # TODO fetch from a given scene ...


def one_by_archetype(archetype_name):
    if (archetype_name not in _archetypes) or (not len(_archetypes[archetype_name])):
        raise ValueError(f'archetype named {archetype_name} not found!')
    adhoc_eid = _archetypes[archetype_name][0]
    return _EntityCls.globalmapping[adhoc_eid]


def add_system(system_func):
    _systems.append(system_func)


def remove_system(system_func):
    _systems.remove(system_func)


def bulk_add_systems(module):
    # hacky but very convenient procedure to add all systems directly from a module
    # :param module: Python module that contains all your game-specific 'system_func' items
    names = module.__all__ if hasattr(module, '__all__') else dir(module)
    bulk = [name for name in names if not name.startswith('_')]
    for syst_name in bulk:
        add_system(getattr(module, syst_name))


def systems_proc(*args):
    if not len(_systems):
        raise ValueError('[PYV/ecs] systems_proc called, but no systems has been added!')
    for system_func in _systems:
        system_func(*args)
