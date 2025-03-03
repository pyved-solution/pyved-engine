"""
testing the .ascii pyv submodule
"""
from pyved_engine import EngineRouter
pyv = EngineRouter.build()
pyv.bootstrap_e()


# - const
CAR_SIZE = 12  # 20, 16, 12, 10, 8 vont fonctionner si c'est le mode HD de pyv qui est actif

IDX_CURSOR = 254
MAXFPS = 50
Y_PAL_POS = 15
PAL = pyv.pal.c64

# - variables
ajouts = dict()
asc_canvas = canv_bsupx = canv_bsupy = None

gameover = False
text_pos = None
tpos = [0, 0]

_scr = None


# -- before starting the main program
def init_game():
    global _scr, asc_canvas, canv_bsupx, canv_bsupy
    pyv.init(1)  # pyv.LOW_RES_MODE)
    asc_canvas = pyv.ascii
    asc_canvas.init(CAR_SIZE)
    canv_bsupx, canv_bsupy = asc_canvas.get_bounds()
    _scr = pyv.get_surface()


def game_loop():
    global asc_canvas, text_pos

    while not pyv.vars.gameover:
        for ev in pyv.event_get():
            print(ev)
            if ev.type == pyv.EngineEvTypes.Quit or (ev.type == pyv.KEYDOWN and ev.key == pyv.keycodes.K_ESCAPE):
                pyv.vars.gameover = True
            elif ev.type == pyv.EngineEvTypes.Mousedown:
                text_pos = list(pyv.ascii.screen_to_cpos(ev.pos))
            elif ev.type == pyv.EngineEvTypes.Keydown:

                if ev.key == pyv.keycodes.K_BACKSPACE:
                    pyv.ascii.increm_char_size()
                    text_pos = None

                elif text_pos is not None and ev.key != pyv.keycodes.K_RETURN:
                    cle = tuple(text_pos)
                    if cle not in ajouts:
                        ajouts[cle] = list()
                    if len(ev.unicode) == 1:
                        ajouts[cle].append(ev.unicode)

        _scr.fill(PAL['blue'])
        # pp = vscreen pygame.mouse.get_pos()
        pp = pyv.get_mouse_coords()
        p = list(asc_canvas.screen_to_cpos(pp))

        # draw the tileset
        for i in range(ord('0'), ord('Z')):
            tpos[0] = (i % 16)
            tpos[1] = (i // 16)
            asc_canvas.put_char(chr(i), tpos, PAL['lightblue'])

        # draw palette
        cf = pyv.ascii.CODE_FILL
        for i in range(16):
            asc_canvas.put_char(cf, (i, Y_PAL_POS), PAL[i])
            asc_canvas.put_char(cf, (i, Y_PAL_POS+1), PAL[i])
            asc_canvas.put_char(cf, (i, Y_PAL_POS+2), PAL[i])

        for adhoc_tpos, aj in ajouts.items():
            if len(aj):
                tmp_pos = list(adhoc_tpos)
                for e in list(aj):  # letter one by one
                    tmp = asc_canvas.put_char(e, tmp_pos, PAL[3], PAL['darkgray'])
                    tmp_pos[0] += 1

        # draw the cursor
        gvpos = [
            (p[0] - 1, p[1] - 1),
            (p[0] + 1, p[1] - 1),
            (p[0] - 1, p[1] + 1),
            (p[0] + 1, p[1] + 1),
        ]
        for elt in ((True, gvpos[0]), (True, gvpos[-1]), (False, gvpos[1]), (False, gvpos[2])):
            flag, popo = elt
            car = '\\' if flag else '/'
            if asc_canvas.is_inside(popo):
                asc_canvas.put_char(car, popo, (250, 11, 33))

        pyv.flip()  # already using the .tick to cap the framerate


if __name__ == '__main__':
    print('running tests (pyv.ascii)')
    init_game()
    game_loop()
    pyv.close_game()
