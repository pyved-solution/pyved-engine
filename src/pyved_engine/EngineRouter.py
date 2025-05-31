"""
GOALS:

- perform a double dependency injection and apply it to the engine
(can add stuff straight into pe_vars) + set screen parameters properly +bootstrap_x
so the engine becomes actionable right away

- play the role of a facade that kinda "merges":
   Engine_constants + Engine_GameDev_api + list_of_EngineEvTypes + all_Keycodes_ever_invented
 so the "concr_engin" folder is really a large blob we don't have to mess with anymore,
 the facade being nicely plugged on top of it

- be a gateway to the AssetsStorage part

- be a gateway to the 'Hub' part of the game engine, so we encapsulate everything
the game dev knows keywords such as "pyv.story" or "pyv.rpg" but should never be
aware of the engine inner structure
"""
import time
from math import degrees as _degrees

from . import hub
from . import state_management
from .AssetsStorage import AssetsStorage
from .abstraction.EvSystem import EngineEvTypes, EvListener, Emitter, EvManager
from .abstraction.LegitPygameEvSource import LegitPygameEvSource
from .concr_engin import core
from .concr_engin import pe_vars
from .concr_engin.pe_vars import KengiEv


# insta-bind so other engine parts can rely on this
pe_vars.ev_manager = EvManager.instance()
pe_vars.engine_events = EngineEvTypes


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

    # Step 3: Inject the dependency
    def __init__(self, sublayer_compo, event_src_class=None):
        # TODO injection to do elsewhere. At module lvl, no? Could be more convenient

        # sublayer_compo has to be follow the "GESublayer" interface (GESublayer=fully abstract class)
        self.bypass_event_type_checking = False
        core.set_sublayer(sublayer_compo)
        if event_src_class:
            self.event_src_class = event_src_class  # a class that inherits from DeepEvSource
        else:
            self.event_src_class = LegitPygameEvSource
        core.save_engine_ref(self)

        # - Below: A neat trick to make our engine compatbile with web ctx.
        # These ar for storing refs on py functions defined in a game cartridge:
        self.endfunc_ref = self.updatefunc_ref = self.beginfunc_ref = None

        # - reste of recent attributes
        self.server_flag = False
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

        self._low_lvl_ev_buffer = list()
        # just a queue for storing events
        self._kev_storage = list()  # kev because KENGI events =high-level, not using pygame ev codes

    def get_sublayer(self):
        return self.low_level_service

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
            # 'data': self._storage.data,
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

    def init(self, lambda_factor: int, maxfps=None, wcaption=None, forced_size=None, cached_paint_ev=None,
             multistate_info=None) -> None:
        """
        CAREFUL it is not the constructor, this is the engine router init func!

        :param lambda_factor: or L, it tells the game engine many pixels we want, to draw our game. L *(160x90)
        :param maxfps:
        :param wcaption:
        :param forced_size:
        :param cached_paint_ev:
        :param multistate_info:
        :return:
        """
        global _engine_rdy, _upscaling_var, _existing_game_ctrl
        print(self.low_level_service.K_F11)
        if self.ready_flag:
            return
        event_source = second_phase_init(self.low_level_service, self.event_src_class, maxfps, wcaption)

        self.ev_source = event_source
        self.low_level_service.fire_up_backend(lambda_factor)
        print('>>>fire_up_backend done')

        # print('setting screen params...')
        # self.low_level_service.set_lambda(lambda_factor)  # pygame display gets activated

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

        y = self.low_level_service.do_screen_param(
            lambda_factor,
            self.low_level_service.get_window_size(),
            cached_paint_ev
        )
        pe_vars.screen = y

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

    static_mapping = {
        256: EngineEvTypes.Quit,  # pygame.QUIT is 256
        32787: EngineEvTypes.Quit,  # for pygame2.0.1+ we also have 32787 -> pygame.WINDOWCLOSE
        771: EngineEvTypes.BasicTextinput,  # pygame.TEXTINPUT

        32768: EngineEvTypes.Activation,  # pygame.ACTIVEEVENT, has "gain" and "state" attributes
        32783: EngineEvTypes.FocusGained,  # pygame.WINDOWFOCUSGAINED
        32784: EngineEvTypes.FocusLost,  # pygame.WINDOWFOCUSLOST

        768: EngineEvTypes.Keydown,  # pygame.KEYDOWN
        769: EngineEvTypes.Keyup,  # pygame.KEYUP
        1024: EngineEvTypes.Mousemotion,  # pygame.MOUSEMOTION
        1025: EngineEvTypes.Mousedown,  # pygame.MOUSEBUTTONDOWN
        1026: EngineEvTypes.Mouseup,  # pygame.MOUSEBUTTONUP

        # gamepad support
        1536: EngineEvTypes.Stickmotion,  # JOYAXISMOTION:  self.joy[event.joy].axis[event.axis] = event.value
        1537: None,  # JOYBALLMOTION:  self.joy[event.joy].ball[event.ball] = event.rel
        1538: EngineEvTypes.GamepadDir,  # JOYHATMOTION:  self.joy[event.joy].hat[event.hat] = event.value
        1539: EngineEvTypes.Gamepaddown,  # JOYBUTTONDOWN: self.joy[event.joy].button[event.button] = 1
        1540: EngineEvTypes.Gamepadup,  # JOYBUTTONUP:  self.joy[event.joy].button[event.button] = 0
    }
    joypad_events_bounds = [1536, 1540]

    mouse_event_types = (EngineEvTypes.Mousedown, EngineEvTypes.Mouseup, EngineEvTypes.Mousemotion)
    Stickmotion_EvT = EngineEvTypes.Stickmotion
    Gamepaddown_EvT = EngineEvTypes.Gamepaddown

    def _map_etype2kengi(self, alien_etype):
        if alien_etype not in self.static_mapping:
            if self.debug_mode:  # notify that there's no conversion
                print('[no conversion] pygame etype=', alien_etype)  # alien_etype.dict)
        else:
            if self.joypad_events_bounds[0] <= alien_etype <= self.joypad_events_bounds[1]:
                pass
                # for convenient gamepad support, we map pygame JOY* in a more specialized way (xbox360 pad support) 2/2
                # else:
            return self.static_mapping[alien_etype]

    def event_get(self):
        cst_joyaxismotion = 1536
        cst_joyballmotion = 1537
        cst_hatmotion = 1538
        cst_joydown = 1539
        cst_joyup = 1540

        del self._kev_storage[:]
        self.ev_source.upload_raw_events(self._low_lvl_ev_buffer)
        # ------------------------
        #  a special event has to be handled
        # ------------------------
        for pyev in self._low_lvl_ev_buffer:
            ev_pyved_repr = None

            if pyev.type == self.low_level_service.VIDEORESIZE:
                # print('-->detection au niveau EngineRoute event resize')
                self.adapt_window_size(pyev.size)
                if self.low_level_service.is_fullscreen():
                    self.low_level_service.fullscreen_flag = False
                    print('forced update of the fullscreen_flag!')

            elif hasattr(pyev, 'key') and pyev.key == self.low_level_service.K_F11:  # F11 interaction
                if pyev.type == 768:  # keydown
                    if not self.low_level_service.is_fullscreen():
                        self.low_level_service.enter_fullscreen()
                    else:
                        self.low_level_service.exit_fullscreen()  # in fact, this will only be called in local ctx

            elif hasattr(pyev, 'key') and pyev.key == self.low_level_service.K_ESCAPE:
                if pyev.type == 768 and self.low_level_service.is_fullscreen():
                    self.low_level_service.exit_fullscreen()
                else:
                    # also: need to forward informations about the escape key
                    ev_pyved_repr = (self._map_etype2kengi(pyev.type), pyev.dict)

            # -----------------------------
            #   convenient gamepad support
            # -----------------------------
            # map pygame JOY* in a specialized way --> xbox360 pad support
            elif pyev.type == cst_joyballmotion:
                pass

            elif pyev.type == cst_hatmotion:  # joy Dpad has been activated
                # <Event(1538-JoyHatMotion {'joy': 0, 'instance_id': 0, 'hat': 0, 'value': (0, 0)})>
                setattr(pyev, 'dir', self.dpad_mapping[pyev.value])  # east, west, etc.
                tmp = list(pyev.value)
                if tmp[1] != 0:
                    tmp[1] *= -1
                pyev.value = pyev.dict['value'] = tuple(tmp)
                ev_pyved_repr = (self._map_etype2kengi(pyev.type), pyev.dict)

            elif pyev.type == cst_joyaxismotion:
                if pyev.axis in (0, 1):
                    self.lstick_val_cache[pyev.axis] = pyev.value
                    ev_pyved_repr = (self.Stickmotion_EvT, {'side': 'left', 'pos': tuple(self.lstick_val_cache)})
                elif pyev.axis in (2, 3):
                    self.rstick_val_cache[-2 + pyev.axis] = pyev.value
                    ev_pyved_repr = (self.Stickmotion_EvT, {'side': 'right', 'pos': tuple(self.rstick_val_cache)})
                elif pyev.axis == 4:
                    ev_pyved_repr = (self.Gamepaddown_EvT, {'button': 'lTrigger', 'value': pyev.value})
                elif pyev.axis == 5:
                    ev_pyved_repr = (self.Gamepaddown_EvT, {'button': 'rTrigger', 'value': pyev.value})

            elif pyev.type in (cst_joydown, cst_joyup):  # joybtdown/joybtup
                pyev.button = self.joy_bt_map[pyev.button]  # change name of the button
                setattr(pyev, 'value', int(pyev.type == cst_joydown))
                ev_pyved_repr = (self._map_etype2kengi(pyev.type), pyev.dict)

            else:  # keypresses, mouse clicks, etc.
                e_type = self._map_etype2kengi(pyev.type)
                e_kwargs = pyev.dict
                if e_type in self.mouse_event_types:
                    e_kwargs['pos'] = self.proj_to_vscreen(e_kwargs['pos'])
                ev_pyved_repr = (e_type, e_kwargs)

            # modify mouse events
            if ev_pyved_repr:  # some events have been ignored/ filtered out
                self._kev_storage.append(KengiEv(ev_pyved_repr[0], **ev_pyved_repr[1]))

        del self._low_lvl_ev_buffer[:]
        return self._kev_storage

    # --- legit pyved functions
    def bootstrap_e(self):
        # TODO use mediator everythime ? instead of EvManager
        # self.mediator = None  # Mediator()
        # need to set it in variables other wise all actor-based games wont work
        from .creep.actors_pattern import Mediator

        pe_vars.mediator = Mediator()  # TODO need to decide if it's instanciated HERE or when client game is launched

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
        from . import umediator
        self._hub.update({
            'umediator': umediator,
            'ecs': ecs,
            'rogue': rogue,
            'states': state_management,
            'defs': defs,
            'gfx': gfx,
            'actors': actors_pattern,
            'game_events_enum': game_events_enum,
            'EvListener': EvListener,
            'Emitter': Emitter,
            'EngineEvTypes': EngineEvTypes,
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
        if not self.server_flag:
            # we always enable sounds, so the engine is ready to load datas
            self.low_level_service.init_sound()

    def process_evq(self):
        pe_vars.mediator.update()

    def set_gameover(self, bval: bool = True):
        pe_vars.gameover = bval
        print('[EngineRouter]->direct signal of game termination received')

    # [a hack for using pyv.umediator]
    # this is handy to replace the default mediator by the modern/more powerful one
    def use_mediator(self, ref_evomed):
        self.bypass_event_type_checking = True
        pe_vars.mediator = ref_evomed
        print('>>PYVED: Now using the experimental Umediator Obj<<')

    def post_ev(self, evtype, **ev_raw_data):
        if self.debug_mode:
            if evtype != 'update' and evtype != 'draw':
                print('>>>>POST', evtype, ev_raw_data)

        if not self.bypass_event_type_checking:
            if evtype not in pe_vars.omega_events:
                raise ValueError(f'trying to post event {evtype}, but this one hasnt been declared')

        if evtype[0] == 'x' and evtype[1] == '_':  # cross event
            pe_vars.mediator.post(evtype, ev_raw_data,
                                  True)  # keep the raw form if we need to push to antother mediator
        else:
            pe_vars.mediator.post(evtype, ev_raw_data, False)

    def get_mouse_coords(self):
        # pygm = _kengi_inj['pygame']
        mpos = self.low_level_service.mouse.get_pos()
        # return _kengi_inj['vscreen'].proj_to_vscreen(mpos)
        return self.proj_to_vscreen(mpos)

    def get_surface(self):
        if pe_vars.screen is None:
            raise LookupError('Cannot provide user with a screen ref, since the engine was not initialized!')
        return pe_vars.screen

    def create_clock(self):
        return self.low_level_service.new_clock_obj()

    def get_ev_manager(self):
        return EvManager.instance()

    def new_font_obj(self, font_src, font_size: int):  # src can be None!
        return self.low_level_service.new_font_obj(font_src, font_size)

    def new_rect_obj(self, *args):  # probably: x, y, w, h
        return self.low_level_service.new_rect_obj(*args)

    def close_game(self):
        if self._storage:  # need to test bc if no assets preloaded, this is None
            self._storage.flush_mem()
        self.low_level_service.quit()

    def surface_create(self, size):
        return self.low_level_service.new_surface_obj(size)

    def surface_rotate(self, img, angle):
        return self.low_level_service.transform.rotate(img, _degrees(-1 * angle))

    @staticmethod
    def run_game(initfunc, updatefunc, endfunc, **kwargs):  # still used by launch_game.py, as of May25
        # -------- WARNING! --------
        # this func can only be called by launch_game.py (local) or via the command line tool
        # this func will NEVER work in the web ctx
        print('<< local ctx - run_game >> DEBUG message, kwargs are:', kwargs)

        # initfunc(None)  # if we remove kwargs, we cant launch a game client with parameters such as host=...
        initfunc(None, **kwargs)
        while not pe_vars.gameover:
            # it is assumed that the developer calls pyv.flip, once per frame,
            # without the engine taking responsability for that
            updatefunc(time.time())
        endfunc(None)

    def __getattr__(self, item):  # a hack so we automatically use: either the hub or the sublayer
        if item in self._hub:
            return self._hub[item]
        return getattr(self.low_level_service, item)

    def flip(self):
        self.low_level_service.vscreen_flip()
        if pe_vars.max_fps:
            pe_vars.clock.tick(pe_vars.max_fps)


# ------------------------------------------------------------+------------------
def get_gs_obj(k):
    return state_management.stack_based_ctrl.get_state_by_code(k)


# vars
_engine_rdy = False
_upscaling_var = None
_scr_init_flag = False


# --- rest of functions ---
def second_phase_init(lower_level_svc, event_source_cls, maxfps=None, wcaption=None):
    global _engine_rdy
    # TODO check when to use mediator
    if maxfps is None:
        y = 60
    else:
        y = maxfps
    pe_vars.max_fps = y

    # here,
    #  we do heavy lifting to bind the pygame event source with the high-level event manager

    # from . import abstraction
    # _pyv_backend = abstraction.build_primalbackend(pe_vars.backend_name)
    # (SIDE-EFFECT: Building the backend also sets kengi_inj.pygame )

    # TODO one item in the long sequence of dep. injections is to be found there:
    #  check where to put the rest
    oneof_pyv_backend = event_source_cls(
        pe_vars.engine_events  # we have to pass:
        # our custom engine's all event types --> to the DeepEventSource we're instantiating,
        # in this way, the DeepEvSource will be able to map its own event codes to PyvedEngine event codes ...
        # tricky but this does work (May25)
    )

    # pbe_identifier: str / values accepted -> to make a valid func. call you would either pass '' or 'web'
    # libbundle_ver: str

    # --------------
    # deprecated:
    #  linking with the ev-source in the web-ctx looked like this
    # --------------
    # elif pbe_identifier == 'web':
    #     if libbundle_ver is None:
    #         if vars.weblib_sig is None or len(vars.weblib_sig) < 1:
    #             raise ValueError('since you use the web backend you HAVE TO specify libbundle_ver !!')
    #         else:
    #             adhoc_ver = vars.weblib_sig
    #     else:
    #         adhoc_ver = libbundle_ver
    #     # assumed that (injector entry 'web_pbackend') => (module==web_pbackend.py & cls==WebPbackend)
    #     # for example:
    #     modulename = 'web_pbackend'
    #     BackendAdhocClass = getattr(_hub.get_injector()[modulename], to_camelcase(modulename))
    #     print('   *inside build_primalbackend*  adhoc class is ', BackendAdhocClass)
    #     # web backends need to ver. info. in great details!
    #     return BackendAdhocClass(adhoc_ver)

    # --------- other dep injection may be this:
    # we shall ALSO
    # define+inject standard transport layers for events that are "cross-events":
    #  - network layer based on sockets
    #  - network layer based on websockets

    # deep_ev_source_cls = 'PygameEvSource'
    # ws_transport_cls = 'WsTransportLocalCtx'

    # then use importlib to load stuff.
    # in that way, we'll be able to reconfigure at runtime!
    # For example:

    # deep_ev_source_cls = 'CanvasBasedEvSource'
    # ws_transport_cls = 'WsTransportWebCtx'

    # CAREFUL: if you dont call the line below,
    # the high level event system wont work (program hanging)
    EvManager.instance().a_event_source = oneof_pyv_backend

    lower_level_svc.init()
    if wcaption:
        lower_level_svc.set_caption(wcaption)
    _engine_rdy = True

    return oneof_pyv_backend  # returns a engine-compatible event source


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
