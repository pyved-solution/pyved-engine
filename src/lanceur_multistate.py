"""
exhibits how one would implement multi-state games with pyved,

based on event sys 4
"""
from pyved_engine import EngineRouter, dependencies
from pyved_engine.abstraction.PygameWrapper import PygameWrapper
from pyved_engine.ifaces.GESublayer import GESublayer

d_container = dependencies.DependencyContainer()
d_container.register('sublayer', PygameWrapper(), interface=GESublayer)


@d_container.inject
def init_engine(sublayer):
    return EngineRouter(sublayer)


pyv = init_engine()
pyv.bootstrap_e()
StackBasedGameCtrl = pyv.states.StateStackCtrl
EngineEvTypes = pyv.EngineEvTypes

# constants
BG_COLOR_ROOM1 = 'salmon'
BG_COLOR_ROOM2 = 'darkblue'
PL_COLOR = (105, 184, 251)
INIT_PL_POS = (240, 135)

# gamestates declaration
GameStates = pyv.struct.enum(
    'Room1',
    'Room2'
)


class Room1Manager(pyv.EvListener):
    def __init__(self):
        super().__init__()
        self.pl_pos = [44, 77]
        self.fresh_st = True
        self.av_pos = list(INIT_PL_POS)
        self.scr_size = pyv.get_surface().get_size()

    def on_event(self, ev):  # source):
        if ev.type == EngineEvTypes.Update:
            self.av_pos[0] = (self.av_pos[0] - 2) % self.scr_size[0]
            self.av_pos[1] = (self.av_pos[1] + 1) % self.scr_size[1]

        elif ev.type == EngineEvTypes.Paint:
            ev.screen.fill(BG_COLOR_ROOM1)
            pyv.draw_circle(
                ev.screen, PL_COLOR, self.av_pos, 15, 0
            )

        elif ev.type == EngineEvTypes.Keydown:
            print('KKK')
            if ev.key == pyv.keycodes.K_SPACE:
                self.fresh_st = False
                self.pev(EngineEvTypes.StatePush, state_ident=GameStates.Room2)
            elif ev.key == pyv.keycodes.K_RETURN and not self.fresh_st:
                self.pev(EngineEvTypes.StatePush, state_ident=GameStates.Room2)
            elif ev.key == pyv.keycodes.K_ESCAPE:
                self.pev(EngineEvTypes.Gameover)


class Room1(pyv.states.BaseGameState):
    def __init__(self, stid):
        super().__init__(stid)
        self.saved_pos = [None, None]
        self.ctrl = None

    def enter(self):
        if self.ctrl is None:
            self.ctrl = Room1Manager()
        self.ctrl.turn_on()

    def pause(self):
        self.ctrl.turn_off()

    def resume(self):
        self.ctrl.turn_on()

    def release(self):
        self.ctrl.turn_off()
        self.ctrl = None


class Room2Manager(pyv.EvListener):
    def __init__(self):
        super().__init__()
        self.av_pos = list(INIT_PL_POS)
        self.scr_size = pyv.get_surface().get_size()

    def on_paint(self, ev):
        ev.screen.fill(BG_COLOR_ROOM2)
        pyv.draw_circle(
            ev.screen, (PL_COLOR[2], PL_COLOR[0], PL_COLOR[1]), self.av_pos, 37, 0
        )

    def on_update(self, ev):
        self.av_pos[0] = (self.av_pos[0] + 3) % self.scr_size[0]
        self.av_pos[1] = (self.av_pos[1] - 1) % self.scr_size[1]

    def on_keydown(self, ev):
        if ev.key == pyv.keycodes.K_BACKSPACE:
            print('pop state')
            self.pev(EngineEvTypes.StatePop)
        elif ev.key == pyv.keycodes.K_ESCAPE:
            self.pev(EngineEvTypes.Gameover)

    def on_quit(self, ev):
        self.pev(EngineEvTypes.Gameover)


class Room2(pyv.states.BaseGameState):
    def __init__(self, stid):
        super().__init__(stid)
        self.saved_pos = [None, None]
        self.ctrl = None

    def enter(self):
        self.ctrl = Room2Manager()
        self.ctrl.turn_on()

    def release(self):
        self.ctrl.turn_off()


if __name__ == '__main__':
    print(" pyv implem of ~~~ Demo B | controls:")
    print(" - RIGHT/LEFT arrow (change state)\n - ENTER (go back)\n - ESCAPE")
    print()
    print('press right first')

    my_stt_infos = (
        GameStates, {
            GameStates.Room1: Room1,
            GameStates.Room2: Room2
        }
    )
    pyv.init(pyv.LOW_RES_MODE, maxfps=40, wcaption='states demo with pyved', multistate_info=my_stt_infos)
    # IMPORTANT: setup events so the engine knows what can be triggered
    # pyv.declare_evs() ->this would work if we use the actor-based logic,
    # however, we are not, so we need to call the LEGACY function on the classic pyved event manager
    pyv.get_ev_manager().setup()

    # let us run the game loop
    game_ctrl = pyv.get_game_ctrl()
    game_ctrl.loop()
    pyv.quit()
