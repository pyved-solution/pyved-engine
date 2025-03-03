from . import pe_vars
from ..concr_engin import core

_vsurface = None
_vsurface_required = True
_is_scr_init = False
game_window_size = None
offsets = [0, 0]

cached_pygame_mod = None  # init from outside when one calls kengi.bootstrap_e
special_flip = 0  # flag, set it to 1 when using web ctx
stored_upscaling = 1

# hopefully i will be able to simplify this:
ctx_emuvram = None
canvas_emuvram = None
canvas_rendering = None
real_pygamescreen = None
screen_rank = 1  # so we can detect whenever its required to update the var in the PAINT engine event

# ------------------------------------
#   old code
# ------------------------------------
_curr_state = None
_loaded_states = dict()
init2_done = False
state_stack = None


def set_upscaling(new_upscal_val):
    global stored_upscaling, _vsurface_required
    if stored_upscaling is not None:
        if int(stored_upscaling) != new_upscal_val:
            stored_upscaling = int(new_upscal_val)
            _vsurface_required = True


def conv_to_vscreen(x, y):
    return int(x / stored_upscaling), int(y / stored_upscaling)


def do_screen_param(lower_level_svc, lambda_factor, display_size, cached_paintev) -> None:
    """
    :param lambda_factor: in the range 1-3. Multiplier applied to 160x90 to comptute the game window (no upscaling)
    :param display_size: how many pixels on the screen e.g. 1920x1080
    :param cached_paintev: can be None or a pyved event that needs to have its .screen attribute set
    """
    global _vsurface, real_pygamescreen
    global _is_scr_init, stored_upscaling, game_window_size
    if _is_scr_init:
        raise RuntimeError('cannot init screen more than once!')

    if not isinstance(lambda_factor, int) or not (0 < lambda_factor < 5):
        raise ValueError('invalid lamda factor!')

    game_window_size = (
        160 * lambda_factor,
        90 * lambda_factor
    )
    real_pygamescreen = lower_level_svc.display.get_surface()
    _vsurface = lower_level_svc.new_surface_obj(game_window_size)
    disp_w, disp_h = display_size

    prev_k_factor = 1
    k_candidate = 2
    while (k_candidate*game_window_size[0]) < disp_w+1 and (k_candidate*game_window_size[1]) < disp_h+1:
        prev_k_factor = k_candidate
        k_candidate += 1
    stored_upscaling = prev_k_factor
    print('disp:', display_size)
    print(f'lambda={lambda_factor}  ; CALC Window {game_window_size}:upscale={stored_upscaling}:offsets={offsets}')
    widget_s = [stored_upscaling*game_window_size[0], stored_upscaling*game_window_size[1]]
    offsets[0], offsets[1] = (disp_w-widget_s[0]) // 2,  (disp_h-widget_s[1]) // 2
    # from here and below,
    # we know the gfx_mode_code is valid 100%
    # conventionw, conventionh = pe_vars.disp_size
    # if gfx_mode_code != 0:
    #     adhoc_upscaling = gfx_mode_code
    #     taille_surf_dessin = int(conventionw / gfx_mode_code), int(conventionh / gfx_mode_code)
    # else:
    #     adhoc_upscaling = 1
    #     taille_surf_dessin = screen_dim
    #     print(adhoc_upscaling, taille_surf_dessin)

    # ---------------------------------
    #  legacy code, not modified in july22. It's complex but
    # it works so dont modify unless you really know what you're doing ;)
    # ---------------------------------
    # if not _is_scr_init:
    #     if stored_upscaling is not None:
    #         pygame_surf_dessin = lower_level_svc.new_surface_obj(taille_surf_dessin)
    #         set_virtual_screen(pygame_surf_dessin)
    #         set_upscaling(adhoc_upscaling)
    #         if gfx_mode_code:
    #             pgscreen = lower_level_svc.set_mode(pe_vars.disp_size)
    #         else:
    #             pgscreen = lower_level_svc.set_mode(taille_surf_dessin)
    #         set_realpygame_screen(pgscreen)
    #
    #     else:  # stored_upscaling wasnt relevant so far =>we usin webctx
    #         _active_state = True
    #         pygame_surf_dessin = lower_level_svc.set_mode(taille_surf_dessin)
    #         set_virtual_screen(pygame_surf_dessin)
    #         # this line is useful for enabling mouse_pos computations even in webCtx
    #         stored_upscaling = float(adhoc_upscaling)

    pe_vars.screen = _vsurface
    if cached_paintev:
        cached_paintev.screen = _vsurface
    _is_scr_init = True


def flip():
    global stored_upscaling, _vsurface

    sl = core.get_sublayer()
    # if not special_flip:  # flag can be off if the extra blit/transform has to disabled (web ctx)
    #     realscreen = sl.display.get_surface()
    #     if 1 == stored_upscaling:
    #         realscreen.blit(pe_vars.screen, (0, 0))
    #     else:
    #         sl.transform.scale(pe_vars.screen, pe_vars.STD_SCR_SIZE, realscreen)
    if stored_upscaling > 1:
        target_size = (stored_upscaling * game_window_size[0], stored_upscaling * game_window_size[1])
        new_surf = sl.transform.scale(pe_vars.screen, target_size)
        real_pygamescreen.blit(new_surf, offsets)
    else:
        real_pygamescreen.blit(_vsurface, offsets)
    sl.display.update()


# def set_canvas_rendering(jsobj):
#     shared.canvas_rendering = jsobj
#
#
# def set_canvas_emu_vram(jsobj):
#     shared.canvas_emuvram = jsobj
#     shared.ctx_emuvram = jsobj.getContext('2d')


# def set_realpygame_screen(ref_surf):
#     global real_pygamescreen
#     if real_pygamescreen:
#         print('warning: set_realpygame_scneen called a 2nd time. Ignoring request')
#         return
#     real_pygamescreen = ref_surf


def set_virtual_screen(ref_surface):
    global screen_rank, defacto_upscaling
    pe_vars.screen = ref_surface
    w = pe_vars.screen.get_size()[0]
    defacto_upscaling = 960 / w
    screen_rank += 1


def proj_to_vscreen(xy_pair):
    global stored_upscaling
    a, b = xy_pair
    x, y = a-offsets[0], b-offsets[1]
    if stored_upscaling > 1:
        return x // stored_upscaling, y // stored_upscaling
    return x, y
