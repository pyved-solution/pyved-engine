"""
Goals of this script:

- to perform a double dependency injection
and apply it to the engine (can add stuff straight into pe_vars)
+ set screen parameters properly +bootstrap_x
so the engine becomes actionable right away

- be a gateway to the AssetsStorage part

- play the role of a facade that kinda "merges":
   Engine_constants + Engine_GameDev_api + list_of_EngineEvTypes + all_Keycodes_ever_invented
 so the "concr_engin" folder is really a large blob we don't have to mess with anymore,
 the facade being nicely plugged on top of it

- be a gateway to the 'Hub' part of the game engine, so we encapsulate everything
the game dev knows keywords such as "pyv.story" or "pyv.rpg" but should never be
aware of the engine inner structure
"""

import time
from math import degrees as _degrees

from . import core
from . import pe_vars
from . import state_management
from .AssetsStorage import AssetsStorage
from .abstraction import EvSystem
from .abstraction import GESublayer, PygameWrapper  # Step 3: Inject the dependency
from .actors_pattern import Mediator
from .compo import vscreen
from .compo.vscreen import flip as _oflip


# insta-bind so other engine parts can rely on this
pe_vars.ev_manager = EvSystem.EvManager.instance()
pe_vars.engine_events = EvSystem.EngineEvTypes


class CodesProxy:
    def __init__(self, ref_sublayer):
        self.sl = ref_sublayer

    def __getattr__(self, item):
        if hasattr(self.sl, item):
            return getattr(self.sl, item)
        print('cannot find keycode:', item)


class EngineRouter:
    """this is basicaly a merged interface to expose high-level functions to the game dev,
    it will be initialized at runtime,
    before loading a game cartridge so the game dev hasn't to worry about that step"""

    # constants that help with engine initialization
    HIGH_RES_MODE, LOW_RES_MODE, RETRO_MODE = 1, 2, 3

    def __init__(self, sublayer_compo: GESublayer):
        core.set_sublayer(sublayer_compo)
        core.save_engine_ref(self)
        self.low_level_service = sublayer_compo

        self.assets_loaded = False
        self._storage = None  # will be instantiated once we call preload_assets
        self.debug_mode = False
        self.ready_flag = False
        # immediate bind
        self._hub = {
            'SpriteGroup': self.low_level_service.sprite.Group,
            'Sprite': self.low_level_service.sprite.Sprite,
            'sprite_collision': self.low_level_service.sprite.spritecollide
        }
        self.ev_source = None

    @classmethod
    def build(cls, sublayer_cls=None):
        """
        Step 4: (usage) Injecting the dependency explicitly
        """
        if sublayer_cls is None:
            engine_depc = PygameWrapper()
        else:
            engine_depc = sublayer_cls()
        return cls(engine_depc)

    def preload_assets(self, metadat_dict, prefix_asset_folder=None, prefix_sound_folder=None):
        self._storage = AssetsStorage(
            self.low_level_service, self.gfx,
            metadat_dict, prefix_asset_folder, prefix_sound_folder
        )
        print('engine status: assets are now available')
        # late bind
        self._hub.update({
            'images': self._storage.images,
            'data': self._storage.data,
            'sounds': self._storage.sounds
        })

    @staticmethod
    def get_game_ctrl():
        return _existing_game_ctrl

    @staticmethod
    def get_version():
        return pe_vars.ENGINE_VERSION_STR

    def init(self, engine_mode_id: int, maxfps=None, wcaption=None, forced_size=None, cached_paint_ev=None, multistate_info=None) -> None:
        rez = self.low_level_service.fire_up_backend(engine_mode_id)
        self.mediator = Mediator()

        global _engine_rdy, _upscaling_var, _existing_game_ctrl
        if engine_mode_id is None:
            mode = self.HIGH_RES_MODE

        if not _engine_rdy:
            self.ev_source = bootstrap_x(self.low_level_service, maxfps, wcaption)

        # back to times when we used the _hub file
        # _hub.modules_activation()  # bootstrap done so... all good to fire-up pyv modules

        if maxfps is None:  # here, we may replace the existing value of maxfps in the engine
            if pe_vars.max_fps:
                pass
            else:
                pe_vars.max_fps = 60
        else:
            pe_vars.max_fps = maxfps

        pe_vars.clock = self.create_clock()

        # TODO find out why we used to do that?
        # if i remove it will it break all?
        # vscreen.cached_pygame_mod = dep_linking.pygame

        print('setting screen params...')
        _screen_param(self.low_level_service, engine_mode_id, forced_size, cached_paint_ev)

        # for retro-compat
        if multistate_info:
            _existing_game_ctrl = state_management.StateStackCtrl(*multistate_info)
        else:
            _existing_game_ctrl = state_management.StateStackCtrl()
        # the lines above have replaced class named: MyGameCtrl()
        self.ready_flag = True
        self.low_level_service.init_sound()  # we always enable sounds

    def draw_circle(self, surface, color_arg, position2d, radius, width=0):
        self.low_level_service.draw_circle(surface, color_arg, position2d, radius, width)

    def draw_rect(self, surface, color, rect4, width, **kwargs):
        self.low_level_service.draw_rect(surface, color, rect4, width)

    def draw_line(self, *args, **kwargs):
        self.low_level_service.draw_line(*args, **kwargs)

    def draw_polygon(self, *args, **kwargs):
        self.low_level_service.draw_polygon(*args, **kwargs)

    def event_get(self):
        return self.ev_source.fetch_kengi_events()

    # --- legit pyved functions
    def bootstrap_e(self):
        self.low_level_service.fire_up_backend(0)  # TODO

        # >>> EXPLICIT
        # from .sublayer_implem import PygameWrapper
        # from . import dep_linking

        # a line required so pyv submodules have a direct access to the sublayer, as well
        # dep_linking.pygame = self.low_level_service

        # all this should be dynamically loaded?
        from .compo import gfx
        from .compo import GameTpl
        from . import custom_struct
        # from . import evsys0
        from .looparts import terrain as _terrain
        from . import pal
        from . import pe_vars as _vars
        from .abstraction.EvSystem import game_events_enum
        from . import actors_pattern
        from . import defs
        self._hub.update({
            'states': state_management,
            'defs': defs,
            'gfx': gfx,
            'actors': actors_pattern,
            'game_events_enum': game_events_enum,
            'EvListener': EvSystem.EvListener,
            'Emitter': EvSystem.Emitter,
            'EngineEvTypes': EvSystem.EngineEvTypes,
            'GameTpl': GameTpl.GameTpl,
            'struct': custom_struct,
            'terrain': _terrain,
            'pal': pal,
            'vars': _vars
        })
        from .looparts import polarbear
        self._hub.update({
            'polarbear': polarbear
        })
        print('---hub in EngineRouter ok')

        from .looparts import ascii as _ascii
        # from .looparts import gui as _gui
        from .looparts import story
        self._hub.update({
            'ascii': _ascii,
            #'gui': _gui,
            'story': story,
        })

        self.keycodes = CodesProxy(self.low_level_service)

    def process_evq(self):
        pe_vars.mediator.update()

    def post_ev(self, evtype, **ev_raw_data):
        if self.debug_mode:
            if evtype != 'update' and evtype != 'draw':
                print('>>>>POST', evtype, ev_raw_data)
        if evtype not in pe_vars.omega_events:
            raise ValueError(f'trying to post event {evtype}, but this one hasnt been declared via pyv.setup_evsys6')
        if evtype[0] == 'x' and evtype[1] == '_':  # cross event
            pe_vars.mediator.post(evtype, ev_raw_data, True)  # keep the raw form if we need to push to antother mediator
        else:
            pe_vars.mediator.post(evtype, ev_raw_data, False)

    def get_mouse_coords(self):
        # pygm = _kengi_inj['pygame']
        mpos = self.low_level_service.mouse.get_pos()
        # return _kengi_inj['vscreen'].proj_to_vscreen(mpos)
        return vscreen.proj_to_vscreen(mpos)

    def get_surface(self):
        if pe_vars.screen is None:
            raise LookupError('Cannot provide user with a screen ref, since the engine was not initialized!')
        return pe_vars.screen

    def create_clock(self):
        return self.low_level_service.new_clock_obj()

    def get_ev_manager(self):
        return EvSystem.EvManager.instance()

    def flip(self):
        _oflip()
        if pe_vars.max_fps:
            pe_vars.clock.tick(pe_vars.max_fps)

    def new_font_obj(self, font_src, font_size: int):  # src can be None!
        return self.low_level_service.new_font_obj(font_src, font_size)

    def new_rect_obj(self, *args):  # probably: x, y, w, h
        return self.low_level_service.new_rect_obj(*args)

    def close_game(self):
        self.low_level_service.quit()

    def surface_create(self, size):
        return self.low_level_service.new_surface_obj(size)

    def surface_rotate(self, img, angle):
        return dep_linking.pygame.transform.rotate(img, _degrees(-1 * angle))

    # - deprecated -----------------------------------
    def run_game(self, initfunc, updatefunc, endfunc):
        # TODO this should be deleted
        #  as it wont work in Track- #1 + web
        experimental_webpy = __import__('sys').platform in ('emscripten', 'wasi')
        if not experimental_webpy:  # Track- #1 : the regular execution
            initfunc(None)
            while not pe_vars.gameover:
                # it's assumed that the developer calls pyv.flip, once per frame,
                # without the engine having to take care of that
                updatefunc(time.time())
            endfunc(None)
        else:  # experimental part: for wasm, etc
            import asyncio
            async def async_run_game():
                initfunc(None)
                while not pe_vars.gameover:
                    updatefunc(time.time())
                    self.flip()  # commit gfx mem to screen, already contains the .tick
                    await asyncio.sleep(0)
                endfunc(None)
            asyncio.run(async_run_game())

    # --- trick to use either the hub or the sublayer
    def __getattr__(self, item):
        if item in self._hub:
            return self._hub[item]

        return getattr(self.low_level_service, item)


# ------------------------------------------------------------+------------------
def get_gs_obj(k):
    return state_management.stack_based_ctrl.get_state_by_code(k)


# vars
_engine_rdy = False
_upscaling_var = None
_scr_init_flag = False


# --- rest of functions ---
def bootstrap_x(lower_level_svc, maxfps=None, wcaption=None, print_ver_info=True):
    global _engine_rdy
    pe_vars.mediator = Mediator()

    if maxfps is None:
        y = 60
    else:
        y = maxfps
    pe_vars.max_fps = y
    # in theory the Pyv backend_name can be hacked prior to a pyv.init() call
    # Now, let's  build a primal backend
    v = pe_vars.ENGINE_VERSION_STR
    if print_ver_info:
        print(f'Booting up pyved-engine {v}...')

    # here,
    #  we do heavy lifting to bind the pygame event source with the high-level event manager

    from . import abstraction

    # (SIDE-EFFECT: Building the backend also sets kengi_inj.pygame )

    _pyv_backend = abstraction.build_primalbackend(pe_vars.backend_name)

    # CAREFUL: if you dont call the line below,
    # the high level event system wont work (program hanging)
    EvSystem.EvManager.instance().a_event_source = _pyv_backend

    lower_level_svc.init()
    if wcaption:
        lower_level_svc.set_caption(wcaption)
    _engine_rdy = True

    return _pyv_backend  # returns a engine-compatible event source


# -------------------------------
#  private functions
# ------------------------------
def _screen_param(lower_level_svc, gfx_mode_code, screen_dim, cached_paintev) -> None:
    """
    :param gfx_mode_code: either 0 for custom scr_size, or any value in [1, 3] for std scr_size with upscaling
    :param screen_dim: can be None or a pair of integers
    :param cached_paintev: can be None or a pyved event that needs to have its .screen attribute set
    """
    print('---dans screen_params -->')
    print('args:', gfx_mode_code, screen_dim, cached_paintev)
    global _scr_init_flag

    # all the error management tied to the "gfx_mode_code" argument has to be done now
    is_valid_gfx_mode = isinstance(gfx_mode_code, int) and 0 <= gfx_mode_code <= 3
    if not is_valid_gfx_mode:
        info_t = type(gfx_mode_code)
        err_msg = f'graphic mode-> {gfx_mode_code}: {info_t}, isnt valid one! Expected type: int'
        raise ValueError(err_msg)
    if gfx_mode_code == 0 and screen_dim is None:
        ValueError(f'Error! Graphic mode 0 implies that a valid "screen_dim" argument is provided by the user!')

    # from here and below,
    # we know the gfx_mode_code is valid 100%
    conventionw, conventionh = pe_vars.disp_size
    if gfx_mode_code != 0:
        adhoc_upscaling = gfx_mode_code
        taille_surf_dessin = int(conventionw / gfx_mode_code), int(conventionh / gfx_mode_code)
    else:
        adhoc_upscaling = 1
        taille_surf_dessin = screen_dim
        print(adhoc_upscaling, taille_surf_dessin)

    # ---------------------------------
    #  legacy code, not modified in july22. It's complex but
    # it works so dont modify unless you really know what you're doing ;)
    # ---------------------------------
    if not _scr_init_flag:
        if vscreen.stored_upscaling is not None:
            pygame_surf_dessin = lower_level_svc.new_surface_obj(taille_surf_dessin)
            vscreen.set_virtual_screen(pygame_surf_dessin)
            vscreen.set_upscaling(adhoc_upscaling)
            if gfx_mode_code:
                pgscreen = lower_level_svc.set_mode(pe_vars.disp_size)
            else:
                pgscreen = lower_level_svc.set_mode(taille_surf_dessin)
            vscreen.set_realpygame_screen(pgscreen)

        else:  # stored_upscaling wasnt relevant so far =>we usin webctx
            _active_state = True
            pygame_surf_dessin = lower_level_svc.set_mode(taille_surf_dessin)
            vscreen.set_virtual_screen(pygame_surf_dessin)
            # this line is useful for enabling mouse_pos computations even in webCtx
            vscreen.stored_upscaling = float(adhoc_upscaling)

        y = pygame_surf_dessin
        pe_vars.screen = y
        if cached_paintev:
            cached_paintev.screen = y
        _scr_init_flag = True


_existing_game_ctrl = None


def close_game():
    pe_vars.gameover = False
    dep_linking.pygame.mixer.quit()
    dep_linking.pygame.quit()

    pe_vars.images.clear()
    pe_vars.csvdata.clear()
    pe_vars.sounds.clear()
    pe_vars.spritesheets.clear()


def curr_state() -> int:
    return state_management.stack_based_ctrl.current


def curr_statename() -> str:
    """
    :returns: a str
    """
    return state_management.stack_based_ctrl.state_code_to_str(
        state_management.stack_based_ctrl.current
    )


# -------
#  september 23 version. It did break upscalin in web ctx
# def flip():
#     global _upscaling_var
#     if _upscaling_var == 2:
#         _hub.pygame.transform.scale(pe_vars.screen, pe_vars.STD_SCR_SIZE, pe_vars.realscreen)
#     elif _upscaling_var == 3:
#         _hub.pygame.transform.scale(pe_vars.screen, pe_vars.STD_SCR_SIZE, pe_vars.realscreen)
#     else:
#         pe_vars.realscreen.blit(pe_vars.screen, (0, 0))
#     _hub.pygame.display.flip()
#     pe_vars.clock.tick(pe_vars.max_fps)
# --------

# very deprec
# def fetch_events():
#     return _hub.pygame.event.get()
#
#
# def get_pressed_keys():
#     return _hub.pygame.key.get_pressed()


# - deprecated
# def load_spritesheet(filepath, tilesize, ck=None):
#     obj = _Spritesheet(filepath)
#     obj.set_infos(tilesize)
#     if ck:
#         obj.colorkey = ck  # could be (255, 0, 255) for example
#     return obj
