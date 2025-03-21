import time
from abc import ABCMeta, abstractmethod
from .. import _hub
from .. import context_bridge as gamedev_api
from ..core.events import EvManager, EngineEvTypes
from .. import vars as engine_vars


class GameTpl(metaclass=ABCMeta):
    """
    the "no name" game template class. It allows to define your game in a quick way,
    by redefining one or several methods: enter, update, exit
    """
    INFO_STOP_MSG = 'kengi.GameTpl->the loop() call has ended.'
    ERR_LOCK_MSG = 'kengi.GameTpl.loop called while SAFETY_LOCK is on!'
    SAFETY_LOCK = False  # can be set to True from outside, if you don't want a game to call .loop()

    def __init__(self):
        self.gameover = False
        self.nxt_game = 'niobepolis'
        self._manager = None

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
        gamedev_api.init(mode=self.get_video_mode())
        self._manager = EvManager.instance()
        self._manager.setup(self.list_game_events())
        self._manager.post(EngineEvTypes.Gamestart)  # pushed to notify that we have really started playing
        gs_enum, mapping = self.list_game_states()
        if gs_enum is not None:
            gamedev_api.declare_game_states(gs_enum, mapping, self)

    def update(self, infot):
        pyg = _hub.pygame
        pk = pyg.key.get_pressed()
        if pk[pyg.K_ESCAPE]:
            self.gameover = True
            return 2, self.nxt_game

        self._manager.post(EngineEvTypes.Update, curr_t=infot)
        self._manager.post(EngineEvTypes.Paint, screen=engine_vars.screen)
        self._manager.update()
        gamedev_api.flip()

    def exit(self, vms=None):
        gamedev_api.close_game()

    def loop(self):
        """
        its forbidden to call .loop() in the web ctx, but its convenient in the local ctx
        if one wants to test a program without using the Kata VM
        :return:
        """
        # lock mechanism, for extra safety so we never call .loop() in the web ctx
        if self.SAFETY_LOCK:
            raise ValueError(self.ERR_LOCK_MSG)

        # use enter, update, exit to handle the global "run game logic"
        self.enter()

        while not self.gameover:
            infot = time.time()
            self.update(infot)
        self.exit()
        print(self.INFO_STOP_MSG)
