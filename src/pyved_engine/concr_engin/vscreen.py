from . import pe_vars as engine_vars
from ..concr_engin import core

_vsurface = None
_vsurface_required = True

cached_pygame_mod = None  # init from outside when one calls kengi.bootstrap_e
special_flip = 0  # flag, set it to 1 when using web ctx
stored_upscaling = 1
defacto_upscaling = None

# hopefully i will be able to simplify this:
ctx_emuvram = None
canvas_emuvram = None
canvas_rendering = None
real_pygamescreen = None
screen_rank = 1  # so we can detect whenever its required to update the var in the PAINT engine event


def set_upscaling(new_upscal_val):
    global stored_upscaling, _vsurface_required
    if stored_upscaling is not None:
        if int(stored_upscaling) != new_upscal_val:
            stored_upscaling = int(new_upscal_val)
            _vsurface_required = True


def flip():
    global _vsurface_required, _vsurface
    if _vsurface_required:
        # TODO
        pass
    sl = core.get_sublayer()
    if not special_flip:  # flag can be off if the extra blit/transform has to disabled (web ctx)
        realscreen = sl.display.get_surface()
        if 1 == stored_upscaling:
            realscreen.blit(engine_vars.screen, (0, 0))
        else:
            sl.transform.scale(engine_vars.screen, engine_vars.STD_SCR_SIZE, realscreen)
    sl.display.update()


# ------------------------------------
#   old code
# ------------------------------------
_curr_state = None
_loaded_states = dict()
init2_done = False
state_stack = None


def conv_to_vscreen(x, y):
    return int(x / defacto_upscaling), int(y / defacto_upscaling)


# def set_canvas_rendering(jsobj):
#     shared.canvas_rendering = jsobj
#
#
# def set_canvas_emu_vram(jsobj):
#     shared.canvas_emuvram = jsobj
#     shared.ctx_emuvram = jsobj.getContext('2d')


def set_realpygame_screen(ref_surf):
    global real_pygamescreen
    if real_pygamescreen:
        print('warning: set_realpygame_scneen called a 2nd time. Ignoring request')
        return
    real_pygamescreen = ref_surf


def set_virtual_screen(ref_surface):
    global screen_rank, defacto_upscaling
    engine_vars.screen = ref_surface
    w = engine_vars.screen.get_size()[0]
    defacto_upscaling = 960/w
    screen_rank += 1


def proj_to_vscreen(xy_pair):
    global stored_upscaling
    if stored_upscaling == 1:
        return xy_pair
    x, y = xy_pair
    return x//stored_upscaling, y//stored_upscaling
