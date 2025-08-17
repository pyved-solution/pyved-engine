from pyved_engine.abstraction import PygameWrapper
import pyved_engine
# Step 4: (usage) Injecting the dependency explicitly:
engine_depc = PygameWrapper()
pyv = pyved_engine.EngineRouter(
    engine_depc
)
pyv.bootstrap_e()


# All constants
BG_COLOR = 'antiquewhite2'
COLOR_PALETTE = {
    0: (144, 105, 151),
    1: (53, 25, 25)
}
DEBUG_MSG = '** computing path **'
INSTR_DEMO = [
    '||KENGI pathfinding demo||', 'Controls: ',
    '- ARROW keys',
    '- SPACE to set blocking/non-blocking',
    '- BACKSPACE to clear last computed result',
    'Most important: ',
    '- when RETURN is pressed the shortest path between {} and {} is computed',
]
MAP_DIM = (14, 9)
OFFSETS = (22, 22)
START_DISP = (30, 30)


class PfDemoModel:
    def __init__(self):
        self.start_pos = [0, 0]
        self.cursor_pos = list(self.start_pos)
        self.end_pos = list(MAP_DIM)
        self.end_pos[0] -= 1
        self.end_pos[1] -= 1
        self.the_map = pyv.struct.BoolMatrix(MAP_DIM)
        self.the_map.set_all(False)  # False means non-blocking
        self.curr_color_code = 0
        self.last_res = None


class PfDemoView(pyv.EvListener):
    def __init__(self, modref):
        super().__init__()
        self._m = modref

    def on_paint(self, ev):
        ev.screen.fill(BG_COLOR)

        for i in range(MAP_DIM[0]):
            for j in range(MAP_DIM[1]):

                pos = list(START_DISP)
                pos[0] += i * OFFSETS[0]
                pos[1] += j * OFFSETS[1]

                # pick a color based on if its blocking or not ; if it belongs to the path or not
                idx = 1 if self._m.the_map.get_val(i, j) else 0
                chosen_color = COLOR_PALETTE[idx]
                if self._m.last_res is not None:
                    if (i, j) in self._m.last_res:
                        chosen_color = 'orange'
                pyv.draw_circle(ev.screen, chosen_color, pos, 10, 0)

        # show the cursor
        a = -10 + self._m.cursor_pos[0] * OFFSETS[0] + START_DISP[0]
        b = -10 + self._m.cursor_pos[1] * OFFSETS[1] + START_DISP[1]
        pyv.draw_rect(ev.screen, 'navyblue', (a, b, 20, 20), 1)


class PfDemoCtrl(pyv.EvListener):
    def __init__(self, modelref):
        super().__init__()
        self._m = modelref

    def move_cursor(self, direct):
        if 'up' == direct:
            if self._m.cursor_pos[1] > 0:
                self._m.cursor_pos[1] -= 1
        elif 'down' == direct:
            if self._m.cursor_pos[1] < MAP_DIM[1] - 1:
                self._m.cursor_pos[1] += 1
        elif 'left' == direct:
            if self._m.cursor_pos[0] > 0:
                self._m.cursor_pos[0] -= 1
        elif 'right' == direct:
            if self._m.cursor_pos[0] < MAP_DIM[0] - 1:
                self._m.cursor_pos[0] += 1

    def on_quit(self, ev):
        self.pev(pyv.EngineEvTypes.Gameover)

    def on_keydown(self, ev):
        if ev.key == pyv.evsys0.K_ESCAPE:
            self.pev(pyv.EngineEvTypes.Gameover)
            print('envoi event Gameover')

        elif ev.key == pyv.evsys0.K_BACKSPACE:
            self._m.last_res = None

        elif ev.key == pyv.evsys0.K_RETURN:
            print(DEBUG_MSG)
            pathfinding_result = pyv.terrain.DijkstraPathfinder.find_path(
                self._m.the_map, self._m.start_pos, self._m.end_pos
            )
            print(pathfinding_result)
            self._m.last_res = pathfinding_result

        elif ev.key == pyv.evsys0.K_SPACE:
            i, j = self._m.cursor_pos
            new_bval = not self._m.the_map.get_val(i, j)
            self._m.the_map.set_val(i, j, new_bval)
            print('new value set on matrix:', new_bval)

        elif ev.key == pyv.evsys0.K_UP:
            self.move_cursor('up')
        elif ev.key == pyv.evsys0.K_DOWN:
            self.move_cursor('down')
        elif ev.key == pyv.evsys0.K_LEFT:
            self.move_cursor('left')
        elif ev.key == pyv.evsys0.K_RIGHT:
            self.move_cursor('right')


class DemoPathfinding(pyv.GameTpl):

    def enter(self, vms=None):
        super().enter(vms)
        model = PfDemoModel()

        # prints out a mini-tutoriel: How to use this demo?
        INSTR_DEMO[-1] = INSTR_DEMO[-1].format(model.start_pos, model.end_pos)
        for line in INSTR_DEMO:
            print(line)
        for recv_obj in (PfDemoView(model), PfDemoCtrl(model)):
            recv_obj.turn_on()

    def get_video_mode(self):
        return 2

    def list_game_events(self):
        return None


if __name__ == '__main__':
    gobj = DemoPathfinding(pyv)
    gobj.loop()
