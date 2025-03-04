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
from .concr_engin import core
from .concr_engin import pe_vars
from . import state_management
from .AssetsStorage import AssetsStorage
from .abstraction import EvSystem
from .abstraction import PygameWrapper  # Step 3: Inject the dependency
# from .actors_pattern import Mediator
from .concr_engin.pe_vars import screen
from .concr_engin import vscreen as screen_mo
from .concr_engin import vscreen
from . import hub

# insta-bind so other engine parts can rely on this
from .creep import actors_pattern

pe_vars.ev_manager = EvSystem.EvManager.instance()
pe_vars.engine_events = EvSystem.EngineEvTypes


class CodesProxy:
    def __init__(self, ref_sublayer):
        self.sl = ref_sublayer

    def __getattr__(self, item):
        if hasattr(self.sl, item):
            return getattr(self.sl, item)
        print(f'[WARNING] Cant find keycode {item} in sublayer compo')


class EngineRouter:
    """this is basicaly a merged interface to expose high-level functions to the game dev,
    it will be initialized at runtime,
    before loading a game cartridge so the game dev hasn't to worry about that step"""

    # constants that help with engine initialization
    HIGH_RES_MODE, LOW_RES_MODE, RETRO_MODE = 1, 2, 3

    def __init__(self, sublayer_compo):  # TODO injection should be done elsewhere
        # sublayer_compo: GESublayer (type)

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
        hub.engine_ref = self

    def get_time(self):
        return time.time()

    def play_sound(self, name, repeat=0):
        self._storage.sounds[name].play(repeat)

    def preload_assets(self, metadat_dict, prefix_asset_folder=None, prefix_sound_folder=None):
        print('***** modern pre-loading *******')
        self._storage = AssetsStorage(
            self.low_level_service, self._hub['gfx'],
            metadat_dict, prefix_asset_folder, prefix_sound_folder
        )
        print('engine status: assets are now available')
        # late bind
        self._hub.update({
            'images': self._storage.images,
            'data': self._storage.data,
            'sounds': self._storage.sounds,
            'spritesheets': self._storage.spritesheets,
            'csvdata': self._storage.csvdata
        })

    @staticmethod
    def get_game_ctrl():
        return _existing_game_ctrl

    @staticmethod
    def get_version():
        return pe_vars.ENGINE_VERSION_STR

    def init(self, engine_mode_id: int, maxfps=None, wcaption=None, forced_size=None, cached_paint_ev=None,
             multistate_info=None) -> None:
        global _engine_rdy, _upscaling_var, _existing_game_ctrl

        if self.ready_flag:
            return
        event_source = snd_part_init(self.low_level_service, maxfps, wcaption)
        self.ev_source = event_source

        rez = self.low_level_service.fire_up_backend(engine_mode_id)

        if engine_mode_id is None:
            mode = self.HIGH_RES_MODE

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

        self.low_level_service.set_mode()  # pygame display gets activated
        print('setting screen params...')

        screen_mo.do_screen_param(
            self.low_level_service, engine_mode_id, self.low_level_service.get_window_size(), cached_paint_ev
        )

        # for retro-compat
        if multistate_info:
            _existing_game_ctrl = state_management.StateStackCtrl(*multistate_info)
        else:
            _existing_game_ctrl = state_management.StateStackCtrl()
        # the lines above have replaced class named: MyGameCtrl()
        self.ready_flag = True

    def draw_circle(self, surface, color_arg, position2d, radius, width=0):
        self.low_level_service.draw_circle(surface, color_arg, position2d, radius, width)

    def draw_rect(self, surface, color, rect4, width=0, **kwargs):
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

        # TODO use mediator everythime ? instead of EvManager
        # self.mediator = None  # Mediator()
        # need to set it in variables other wise all actor-based games wont work
        from .creep.actors_pattern import Mediator
        pe_vars.mediator = Mediator()

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
        from .concr_engin import pe_vars as _vars
        from .abstraction.EvSystem import game_events_enum
        from .creep import actors_pattern
        from . import defs
        from .patterns import ecs
        from .looparts import rogue
        self._hub.update({
            'ecs': ecs,
            'rogue': rogue,
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

        from .looparts import ascii as _ascii
        # from .looparts import gui as _gui
        # from .m_ext import story
        self._hub.update({
            'ascii': _ascii,
            # 'gui': _gui,
            # 'story': story,
        })

        print('---/-/////////////////------------')
        print('Hub in EngineRouter has been updated')

        self.keycodes = CodesProxy(self.low_level_service)
        # we always enable sounds, so the engine is ready to load datas
        self.low_level_service.init_sound()

    def process_evq(self):
        pe_vars.mediator.update()

    def set_gameover(self, bval: bool = True):
        pe_vars.gameover = bval
        print('[EngineRouter]->direct signal of game termination received')

    def post_ev(self, evtype, **ev_raw_data):
        if self.debug_mode:
            if evtype != 'update' and evtype != 'draw':
                print('>>>>POST', evtype, ev_raw_data)
        if evtype not in pe_vars.omega_events:
            raise ValueError(f'trying to post event {evtype}, but this one hasnt been declared via pyv.setup_evsys6')
        if evtype[0] == 'x' and evtype[1] == '_':  # cross event
            pe_vars.mediator.post(evtype, ev_raw_data,
                                  True)  # keep the raw form if we need to push to antother mediator
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
        screen_mo.flip()
        if pe_vars.max_fps:
            pe_vars.clock.tick(pe_vars.max_fps)

    def new_font_obj(self, font_src, font_size: int):  # src can be None!
        return self.low_level_service.new_font_obj(font_src, font_size)

    def new_rect_obj(self, *args):  # probably: x, y, w, h
        return self.low_level_service.new_rect_obj(*args)

    def close_game(self):
        self.low_level_service.quit()

        # pe_vars.gameover = False
        # dep_linking.pygame.mixer.quit()
        # dep_linking.pygame.quit()
        self.images.clear()
        self.csvdata.clear()
        self.sounds.clear()
        self.spritesheets.clear()

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
def snd_part_init(lower_level_svc, maxfps=None, wcaption=None, print_ver_info=True):
    global _engine_rdy
    # TODO check when to use mediator
    if maxfps is None:
        y = 60
    else:
        y = maxfps
    pe_vars.max_fps = y

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


_existing_game_ctrl = None


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
