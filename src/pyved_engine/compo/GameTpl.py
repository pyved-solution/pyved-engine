import time
from abc import ABCMeta, abstractmethod

from .. import pe_vars as engine_vars
from ..abstraction.EvSystem import EvManager, EngineEvTypes


class GameTpl(metaclass=ABCMeta):
    """
    the "no name" game template class. It allows to define your game in a quick way,
    by redefining one or several methods: enter, update, exit
    """
    INFO_STOP_MSG = 'kengi.GameTpl->the loop() call has ended.'
    ERR_LOCK_MSG = 'kengi.GameTpl.loop called while SAFETY_LOCK is on!'
    SAFETY_LOCK = False  # can be set to True from outside, if you don't want a game to call .loop()

    def __init__(self, engine_inst):
        self.nxt_game = 'niobepolis'
        self._manager = None
        self.engine = engine_inst

    @abstractmethod
    def get_video_mode(self):
        raise NotImplementedError

    @abstractmethod
    def list_game_events(self):
        """
        :return: all specific/custom game events. If nothing applies you can return None or []
        """
        raise NotImplementedError

    def list_game_states(self):
        """
        :return: all specific states(scenes) of the game!
        None, None should be returned as a signal that game doesnt need to use the state manager!
        """
        return None, None

    def enter(self, vms=None):
        """
        Careful if you redefine this:
        one *HAS TO*
         - init video
         - set the gameticker
         - set the _manager attribute (bind the ev manager to self._manager)
         - call self._manager.setup(...) with args
        """
        self.engine.init(self.get_video_mode())
        self._manager = EvManager.instance()
        print('manager:', self._manager)
        self._manager.setup(self.list_game_events())
        self._manager.post(EngineEvTypes.Gamestart)  # pushed to notify that we have really started playing
        gs_enum, mapping = self.list_game_states()
        if gs_enum is not None:
            self.engine.declare_game_states(gs_enum, mapping, self)

    def update(self, infot):
        pk = self.engine.get_pressed()
        self._manager.post(EngineEvTypes.Update, curr_t=infot)
        self._manager.post(EngineEvTypes.Paint, screen=engine_vars.screen)
        self._manager.update()
        self.engine.flip()

    def exit(self, vms=None):
        self.engine.close_game()

    def loop(self):
        """
        its forbidden to call .loop() in the web ctx, but its convenient in the local ctx
        if one wants to test a program without using the Kata VM
        :return:
        """
        print('dans loop')
        # lock mechanism, for extra safety so we never call .loop() in the web ctx
        if self.SAFETY_LOCK:
            raise ValueError(self.ERR_LOCK_MSG)

        # use enter, update, exit to handle the global "run game logic"
        self.enter()
        while not engine_vars.gameover:
            infot = time.time()
            self.update(infot)
        self.exit()
        print(self.INFO_STOP_MSG)
