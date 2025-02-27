import abc

from .core import underscore_format


class Objectifier:
    def __init__(self, data):
        self.__dict__.update(data)


def enum_builder_generic(to_upper, starting_index, *sequential, **extra_manset_codes):
    domaine = range(starting_index, len(sequential) + starting_index)
    enums = dict(zip(sequential, domaine))

    # can update the dictionnary if some codes are manually set
    # *BUT*
    # be careful, this must be used wisely and
    # one has to print warnings in case codes are overriden by the user
    if len(extra_manset_codes)>0:
        for chosen_name, code in extra_manset_codes.items():
            if code in enums.values():
                for prevname, c in enums.items():
                    if c == code:
                        break
                old = prevname
                del enums[prevname]
                new = chosen_name
                print(f'### warning! enum_builder_generic overrides the id {code} ( {old}-->{new} )')
            enums[chosen_name] = code

    tmp_inv_map = {v: k for k, v in enums.items()}
    if to_upper:
        tmp = dict()
        for k, v in enums.items():
            if k == 'inv_map' or k == 'all_codes':
                continue
            tmp[k.upper()] = v
        enums = tmp

    enums['inv_map'] = tmp_inv_map
    enums['last_code'] = len(sequential) + starting_index - 1
    enums['all_codes'] = tuple(tmp_inv_map.keys())
    return type('Enum', (), enums)


def enum_from_n(n, *sequential, **named):
    return enum_builder_generic(False, n, *sequential, **named)


def enum(*sequential, **named):
    """
    the most used enum builder
    """
    return enum_from_n(0, *sequential, **named)


# --- trick from stackoverflow...
class abstractclassmethod(classmethod):
    __isabstractmethod__ = True

    def __init__(self, fcallable):
        fcallable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(fcallable)


# ------------------------------- matrices -------------------------------
class BaseMatrix(object):
    """
    classe ABSTRAITE
    représentation 1d dune matrice bidimensionnelle de taille connue
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, matr_size, li1d_val_init=None):
        self.width, self.height = matr_size
        nb_elem = self.width * self.height
        if li1d_val_init is not None:
            if len(li1d_val_init) != nb_elem:
                raise ValueError('val pour init matrice incoherentes')
            for elt in li1d_val_init:
                if not self.__class__.isValidValue(elt):
                    raise ValueError('val type doesnt match matrix type, elt={}'.format(elt))
            self.repr_1d = li1d_val_init
        else:
            self.repr_1d = [self.__class__.defaultValue()] * nb_elem

    @abstractclassmethod
    def defaultValue(cls):
        pass

    @abstractclassmethod
    def isValidValue(cls, val):
        pass

    def get_val(self, i, j):
        if self.is_out(i, j):
            raise ValueError('coords {} {} out of bounds for the current matrix'.format(i, j))
        adhoc_ind = j * self.width + i
        return self.repr_1d[adhoc_ind]

    def set_val(self, i, j, val):
        if not self.__class__.isValidValue(val):
            raise ValueError(
                'val {} incompatible avec le type de matrice utilisé ({})'.format(val, self.__class__.__name__)
            )
        ind = j * self.width + i
        self.repr_1d[ind] = val

    def set_all(self, val):
        for i in range(self.width):
            for j in range(self.height):
                self.set_val(i, j, val)

    def is_out(self, i, j):
        return not (0 <= i < self.width and 0 <= j < self.height)

    def get_size(self):
        return self.width, self.height

    def __str__(self):
        res = '{} x {} matrix'.format(self.width, self.height)
        res += "\n"
        for j in range(self.height):
            for i in range(self.width):
                ind = j * self.width + i
                res += '  {}'.format(self.repr_1d[ind])
            res += "\n"
        return res


class BoolMatrix(BaseMatrix):
    # --- redefinition de 2 methodes venant den haut
    @classmethod
    def defaultValue(cls):
        return True

    @classmethod
    def isValidValue(cls, val):
        return isinstance(val, bool)


class IntegerMatrix(BaseMatrix):
    """
    modélise une matrice d'entiers. Par défaut, toutes les cellules sont à 0. On redef 2 methodes venant den haut
    """
    @classmethod
    def defaultValue(cls):
        return 0

    @classmethod
    def isValidValue(cls, val):
        return (val is None) or isinstance(val, int)
# --------------- end of matrices -------------------------


class Stack:
    def __init__(self, given_seq=None):
        if given_seq is None:
            self.fifo_list = []
        else:
            self.fifo_list = list(given_seq)

    def push(self, element):
        self.fifo_list.append(element)
        # - debug
        # print()
        # print('PUSH')
        # print('etat de pile {}'.format(self.fifo_list))

    def top_down_trav(self):
        return reversed(self.fifo_list)

    def bottom_up_trav(self):
        return self.fifo_list

    def pop(self):
        try:
            tmp = self.fifo_list.pop()
            res = tmp
        except IndexError:
            res = None  # the stack's already empty

        return res

    def peek(self):
        try:
            return self.fifo_list[-1]
        except IndexError:
            return None  # the stack's empty

    def count(self):
        return len(self.fifo_list)


# --------------------------------------------
#  generic tree structure
# --------------------------------------------
class Tree:
    def __init__(self, rootnode_ref):
        self._root = rootnode_ref
        self.allnodesinfo = set()  # do not modify this member directly

    @property
    def root(self):
        return self._root

    # TODO
    # @root.setter
    # def root(self, noderef):
    #     self._root = noderef

    def append_value(self, value, parent_node):
        if parent_node is None:
            raise ValueError('[Tree]Error - Cannot use append_value to create a root node!')
        if parent_node not in self.allnodesinfo:
            raise ValueError('[Tree]Error - Trying to append value to a node that doesnt exist!')
        return TreeNode(value, parent_node)

    @property
    def count(self):
        return len(self.allnodesinfo)

    def has_node(self, node_ref):
        return node_ref in self.allnodesinfo

    def node_by_content(self, needle_value):
        """
        returns None if needle_value isnt found
        """
        for node_ref in self.allnodesinfo:
            if needle_value == node_ref.value:
                return node_ref

    def sub_tree(self, node_ref):
        raise NotImplementedError  # TODO, use node cloning

    def __str__(self):
        r = ''
        for node in self._root.traverse():
            d = node.depth
            v = node.value
            spstr = ''.join([' ' for _ in range(d)])
            r += f'{spstr}node[depth:{d}] val={v}' + '\n'
        return r

    # def cut_from_node(self, ref_node):
    #     if ref_node == self.root:
    #         raise ValueError('empty tree not allowed')
    #
    #     if not ref_node.is_leaf():
    #         # if node has childs, we shall cut the whole branch
    #         for c in ref_node.childs:
    #             self.cut_from_node(c)
    #
    #     ref_node.parent.childs.remove(ref_node)
    #     self.__allnodes.remove(ref_node)


class TreeNode:
    def __init__(self, value, parent_ref):
        """
        set parent_ref to None,
        in order to create a root node + the associated tree.

        Important remark: this class doesnt allow for the creation of 'headless' nodes,
        that is nodes that are not bound to a given Tree! It simplifies the implementation
        as it prevents the dev from doing things that make no sense. For instance: trying to
        add an existing node (say, the 1st child of root) to the 2nd child of root
            r
          /  \
         a    b
        doing b.add_child(a) should be always be forbidden,
        so we dont implement an add_child method.
        """
        self.value = value  # data

        if parent_ref:
            self.parent = parent_ref
            self.parent.children.append(self)
            self.tree_ref = parent_ref.tree_ref
        else:
            self.parent = None
            self.tree_ref = Tree(self)
        self.tree_ref.allnodesinfo.add(self)

        self.children = list()  # references to other nodes

    @property
    def depth(self):
        cpt = 0
        r = self
        while not r.is_root():
            r = r.parent
            cpt += 1
        return cpt

    @property
    def child_count(self):
        return len(self.children)

    def is_root(self):
        return self.parent is None

    def is_leaf(self):
        return len(self.children) == 0

    def remove_child(self, child_node):
        # removes parent-child relationship
        if self.tree_ref.has_node(child_node):
            self.children = [child for child in self.children if child is not child_node]
            self.tree_ref.allnodesinfo.remove(child_node)
        else:
            print('***[TreeNode] warning trying to remove a child that does not exist***')

    def traverse(self):
        visited_nodes = list()
        nodes_to_visit = [self]
        while len(nodes_to_visit) > 0:
            curr_node = nodes_to_visit.pop(0)
            visited_nodes.append(curr_node)
            nodes_to_visit += curr_node.children
        return visited_nodes


class StContainer:
    """
    contient toutes les instances de classes qui dérivent de BaseGameState
    """

    def __init__(self):
        self.__setup_done = False
        self.assoc_id_state_obj = dict()

    def setup(self, enum_game_states, stmapping, pymodule=None):
        self.__setup_done = True

        # - initialisation d'après paramètre type: core.enum
        if stmapping:  # but = charger la classe deja identifiee en memoire
            for state_ident, adhoc_cls in stmapping.items():
                print('creating state:', adhoc_cls.__name__)
                obj = adhoc_cls(state_ident)

                # if needed: enable Kata bios state
                if -1 == state_ident:
                    obj.glvars_module = pymodule  # TODO fix architecture,
                    # StContainer shouldnt know details bout SDK feat

                # the regular op
                self.assoc_id_state_obj[state_ident] = obj
        else:

            # old code
            for id_choisi, nom_etat in enum_game_states.inv_map.items():
                class_name = nom_etat + 'State'
                self._auto_find_statecls(id_choisi, nom_etat, class_name)

    def _auto_find_statecls(self, id_choisi, nom_etat, nom_cls):
        pymodule_name = underscore_format(nom_etat)
        pythonpath = 'app.{}.state'.format(pymodule_name)
        print('StContainer is loading a new game state...')
        try:
            pymodule = __import__(pythonpath, fromlist=[nom_cls])
            adhoc_cls = getattr(pymodule, nom_cls)  # class has been retrieved -> ok

            obj = adhoc_cls(id_choisi, nom_etat)
            self.assoc_id_state_obj[id_choisi] = obj

        except ImportError as exc:
            print('ERR: Cannot import State Cls!')
            print()
            print('adhoc module name(conv. to underscore format)={}'.format(pymodule_name))
            print('full path for finding class={}'.format(pythonpath))
            print('target class={}'.format(nom_cls))

    def retrieve(self, identifiant):
        """
        :param identifiant: peut-être aussi bien le code (int) que le nom de classe dédiée (e.g. PlayState)
        :return: instance de BaseGameState
        """

        # construction par nom ou identifiant entier
        # TODO rétablir recherche par nom et non par code...

        # if isinstance(identifiant, str):
        #     gamestate_id = None
        #     for num_id, nom in state_listing.items():
        #         if nom == identifiant:
        #             gamestate_id = num_id
        #             break
        #     if gamestate_id is None:
        #         assert 0, "state name not found: " + identifiant
        # else:
        #     gamestate_id = identifiant
        gamestate_id = identifiant
        return self.assoc_id_state_obj[gamestate_id]
