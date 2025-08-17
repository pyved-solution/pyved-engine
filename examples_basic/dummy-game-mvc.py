"""
showcasing the "dummy game" but we make use of the MVC pattern here.
This file will help you in understanding how the pattern should be applied to
your particular game idea
"""
from pyved_engine import EngineRouter
from pyved_engine.abstraction.PygameWrapper import PygameWrapper
pyv = EngineRouter(PygameWrapper())

pyv.bootstrap_e()


# from katagames_engine.foundation.pbackends import build_primalbackend
# ev2 = pyv.event2
MyEvents = pyv.game_events_enum((
    'PlayerMovement',  # contains attributes x, y
    'ColorChange',  # contains color_code
))

# here we wish to showcase "demo using events+the mvc pattern"
EngineEvTypes = pyv.EngineEvTypes


# ------------------
#  this software variant produces the same result as any dummy-pattern-none,
#  but it uses the M.V.C. pattern cf. the 3 classes below
# -----------------
class GameState(pyv.Emitter):
    # As a rule of thumb: all classes that model some aspect of your software should inherit from CogObj
    """
    the model
    """
    def __init__(self):
        super().__init__()
        self.av_pos = [240, 135]
        self.av_y_speed = 0
        self.curr_color_code = 0
        self.bounds = pyv.get_surface().get_size()

    def refresh_avatar_pos(self):
        self.av_pos[1] = (self.av_pos[1] + self.av_y_speed) % self.bounds[1]
        # dispatch info
        self.pev(MyEvents.PlayerMovement, x=self.av_pos[0], y=self.av_pos[1])

    def switch_avatar_color(self):
        self.curr_color_code = (self.curr_color_code + 1) % 2
        self.pev(MyEvents.ColorChange, color_code=self.curr_color_code)


class GameView(pyv.EvListener):
    """
    the view
    """
    BG_COLOR = 'antiquewhite2'

    def __init__(self, gs):
        super().__init__()
        self._col_palette = {
            0: (244, 105, 251),
            1: (105, 184, 251)
        }
        self.pl_screen_pos = list(gs.av_pos)
        self.pl_color = self._col_palette[gs.curr_color_code]

    def on_player_movement(self, ev):
        self.pl_screen_pos[:] = [ev.x, ev.y]

    def on_color_change(self, ev):
        self.pl_color = self._col_palette[ev.color_code]

    def on_paint(self, ev):
        screen = pyv.get_surface()
        screen.fill(self.BG_COLOR)
        pyv.draw_circle(ev.screen, self.pl_color, self.pl_screen_pos, 15, 0)


class DemoCtrl(pyv.EvListener):
    """
    the controller
    """
    def __init__(self, gs):
        super().__init__()
        self.state = gs

    # def on_toto(self, ev):
    #    pass

    def on_update(self, ev):
        self.state.refresh_avatar_pos()

    def on_quit(self, ev):
        pyv.vars.gameover = True

    def on_keyup(self, ev):
        prkeys = pyv.get_pressed()
        if (not prkeys[pyv.keycodes.K_UP]) and (not prkeys[pyv.keycodes.K_DOWN]):
            self.state.av_y_speed = 0

    def on_keydown(self, ev):
        if ev.key == pyv.keycodes.K_ESCAPE:
            pyv.vars.gameover = True
            print('dummy good bye')
        elif ev.key == pyv.keycodes.K_SPACE:
            self.state.switch_avatar_color()
        elif ev.key == pyv.keycodes.K_UP:
            self.state.av_y_speed = -1
        elif ev.key == pyv.keycodes.K_DOWN:
            self.state.av_y_speed = 1


def play_game():
    """
    using the built-in event manager + game controller to execute the game
    """
    pyv.init(pyv.LOW_RES_MODE, wcaption='hello')
    pyv.get_ev_manager().setup(MyEvents)

    game_st = GameState()
    # unified
    game_ctrl = pyv.get_game_ctrl()

    receivers = [DemoCtrl(game_st), GameView(game_st)]

    # MANDATORY: setup the new event system!
    ev_m = pyv.get_ev_manager()
    ev_m.setup(MyEvents)
    # in case you need debug infos:
    ev_m.debug_mode = True

    for r in receivers:
        r.turn_on()  # listen to incoming events
    game_ctrl.loop()  # will automatically call .turn_on() on the game_ctrl,
    # then run a standard game loop
    pyv.close_game()


if __name__ == '__main__':
    print("~~~ pyv events+mvc variant of Demo A~~~")
    print(" Controls: UP/DOWN arrow, SPACE, ESCAPE")
    print('~~~ ~~~')
    play_game()
    print('Clean exit-')
