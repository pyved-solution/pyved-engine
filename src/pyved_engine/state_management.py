import time

from . import pe_vars
from ._classes import BaseGameState
from .compo import vscreen
from .custom_struct import Stack, StContainer, enum
from .abstraction import EvSystem


multistite_flag = False
stack_based_ctrl = None
state_stack = None
_DefaultGsList = enum(
    'Room1',
)


class _DefaultRoomClass(BaseGameState):
    def __init__(self, stid):
        super().__init__(stid)

    def enter(self):
        pass

    def release(self):
        pass


_default_st_mapping = {  # bind identifier to class
    _DefaultGsList.Room1: _DefaultRoomClass
}


class StateStackCtrl(EvSystem.EvListener):
    """
    used to manage the game state but also provide the very basic game_loop
    """
    INFO_STOP_LOOP_MSG = 'we leave the game loop now (StateStackCtrl class)'

    def __init__(self, all_gs=None, st_to_cls_mapping=None):
        super().__init__()
        self._clock = pe_vars.clock

        self._gs_omega = _DefaultGsList if all_gs is None else all_gs
        adhoc_mapping = _default_st_mapping if all_gs is None else st_to_cls_mapping

        self._stack = Stack()
        # CONVENTION: the first of the enum <=> the init gamestate id !
        self.first_state_id = self._gs_omega.all_codes[0]
        self._st_container = StContainer()
        self._st_container.setup(self._gs_omega, adhoc_mapping, None)
        self.__state_stack = Stack()

    def get_state_by_code(self, k):
        return self._st_container.retrieve(k)

    def state_code_to_str(self, x):
        return self._gs_omega.inv_map[x]

    def turn_on(self):
        super().turn_on()
        print('>>>>>>>>>* Note: State stack is OPERATIONAL *')

    @property
    def current(self):
        return self.__state_stack.peek()

    # (it's a private method)
    # WARNING: never, ever call that method without a kind of follow-up
    def __only_the_pop_part(self):
        tmp = self.__state_stack.pop()
        state_obj = self._st_container.retrieve(tmp)
        state_obj.release()

    def _change_state(self, state_obj):
        self.__only_the_pop_part()
        self.__state_stack.push(state_obj.get_id())
        state_obj.enter()

    def _push_state(self, state_obj):
        tmp = self.__state_stack.peek()
        curr_state = self._st_container.retrieve(tmp)
        curr_state.pause()
        self.__state_stack.push(state_obj.get_id())
        state_obj.enter()

    def _pop_state(self):
        self.__only_the_pop_part()
        print('remains:', self.__state_stack.count())
        if self.__state_stack.count() > 0:
            tmp = self.__state_stack.peek()
            state_obj = self._st_container.retrieve(tmp)
            state_obj.resume()
        else:
            pe_vars.gameover = True

    # --------------------
    #  CALLBACKS
    # --------------------
    def on_gamestart(self, ev):
        self.__state_stack.push(self.first_state_id)
        self._st_container.retrieve(self.first_state_id).enter()
        print('>>>pushin a state on the stack')

    def on_gameover(self, ev):
        print('poppin all')
        while self.__state_stack.count() > 0:
            self._pop_state()

    def on_state_change(self, ev):
        state_obj = self._st_container.retrieve(ev.state_ident)
        self._change_state(state_obj)

    def on_state_push(self, ev):
        state_obj = self._st_container.retrieve(ev.state_ident)
        self._push_state(state_obj)

    def on_state_pop(self, ev):
        self._pop_state()

    # - helper function -
    def loop(self) -> None:
        """
        its forbidden to call .loop() in the web ctx, but its convenient in the local ctx
        if one wants to test a program without harnessing the whole pyVM
        """
        print('*Warning! Never use .loop in the web Ctx*')
        self.turn_on()
        e_types = EvSystem.EngineEvTypes

        self.pev(e_types.Gamestart)  # ensure we will call .enten() on the initial/eden state
        while not pe_vars.gameover:
            infot = time.time()
            self.pev(e_types.Update, curr_t=infot)
            self.pev(e_types.Paint, screen=pe_vars.screen)
            self._manager.update()
            vscreen.flip()
            self._clock.tick(pe_vars.max_fps)
        # TODO shall we ensure we have pop'ed every single state?
        # self.proper_exit()
        print(self.__class__.INFO_STOP_LOOP_MSG)


def declare_game_states(gs_enum, assoc_gscode_gscls):
    """
    :param gs_enum: enum of every single gamestate code
    :param assoc_gscode_gscls: a dict that binds a gamestate code to a gamestate class
    :param refgame: ref on the object whose type inherits from pyv.GameTpl
    """
    global stack_based_ctrl, multistate_flag

    multistate_flag = True
    stack_based_ctrl = StateStackCtrl(gs_enum, assoc_gscode_gscls)
    # activation Autho!
    stack_based_ctrl.turn_on()
