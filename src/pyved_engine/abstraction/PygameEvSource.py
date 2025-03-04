from ..concr_engin import vscreen
from ..ifaces.DeepEvSource import DeepEvSource
from ..concr_engin.pe_vars import EngineEvTypes
from ..concr_engin.pe_vars import KengiEv


class PygameEvSource(DeepEvSource):
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

    joy_bt_map = {
        0: 'A',
        1: 'B',
        2: 'X',
        3: 'Y',
        4: 'lB',
        5: 'rB',
        6: 'Back',
        7: 'Start'
    }
    dpad_mapping = {
        (0, 0): None,
        (0, 1): 'north',
        (1, 0): 'east',
        (0, -1): 'south',
        (-1, 0): 'west',
        (1, 1): 'north-east',
        (-1, 1): 'north-west',
        (-1, -1): 'south-west',
        (1, -1): 'south-east'
    }

    def __init__(self):
        import pygame as _genuine_pyg

        # TODO fix code temporaire qui est là pr améliorer (code layout) du moteur
        # injector = _hub.get_injector()
        # injector.set('pygame', _genuine_pyg)

        self._pygame_mod = _genuine_pyg
        self.debug_mode = False
        self._ev_storage = list()
        self.pyg_jm = None  # model for joystickS
        self.lstick_val_cache = [0.0, 0.0]
        self.rstick_val_cache = [0.0, 0.0]

    def joystick_init(self, idj):
        self.pyg_jm = self._pygame_mod.joystick.Joystick(idj)
        self.pyg_jm.init()

    def joystick_info(self, idj):
        return self.pyg_jm.get_name()

    def joystick_count(self):
        return self._pygame_mod.joystick.get_count()

    def _map_etype2kengi(self, alien_etype):
        if alien_etype not in self.__class__.static_mapping:
            if self.debug_mode:  # notify that there's no conversion
                print('[no conversion] pygame etype=', alien_etype)  # alien_etype.dict)
        else:
            if self.joypad_events_bounds[0] <= alien_etype <= self.joypad_events_bounds[1]:
                pass
                # for convenient gamepad support, we map pygame JOY* in a more specialized way (xbox360 pad support) 2/2
                # else:
            return self.__class__.static_mapping[alien_etype]

    def fetch_kengi_events(self):
        cst_joyaxismotion = 1536
        cst_joyballmotion = 1537
        cst_hatmotion = 1538
        cst_joydown = 1539
        cst_joyup = 1540

        raw_pyg_events = self._pygame_mod.event.get()
        del self._ev_storage[:]

        # ------------------------
        #  a very special event has to be handled
        # ------------------------
        # type=VIDEORESIZE args=(size, w, h)

        for pyev in raw_pyg_events:
            r = None
            if pyev.type == self._pygame_mod.VIDEORESIZE:
                vscreen.refresh_screen_params(pyev.size)  #, pyev.w, pyev.h)

            # for convenient gamepad support, we will
            # map pygame JOY* in a specialized way (xbox360 pad support)
            elif pyev.type == cst_joyaxismotion:
                if pyev.axis in (0, 1):
                    self.lstick_val_cache[pyev.axis] = pyev.value
                    r = (EngineEvTypes.Stickmotion, {'side': 'left', 'pos': tuple(self.lstick_val_cache)})

                elif pyev.axis in (2, 3):
                    self.rstick_val_cache[-2 + pyev.axis] = pyev.value
                    r = (EngineEvTypes.Stickmotion, {'side': 'right', 'pos': tuple(self.rstick_val_cache)})

                elif pyev.axis == 4:
                    r = (EngineEvTypes.Gamepaddown, {'button': 'lTrigger', 'value': pyev.value})

                elif pyev.axis == 5:
                    r = (EngineEvTypes.Gamepaddown, {'button': 'rTrigger', 'value': pyev.value})

            elif pyev.type == cst_joyballmotion:
                # ignore
                pass

            elif pyev.type == cst_hatmotion:  # joy Dpad has been activated
                # <Event(1538-JoyHatMotion {'joy': 0, 'instance_id': 0, 'hat': 0, 'value': (0, 0)})>
                setattr(pyev, 'dir', self.dpad_mapping[pyev.value])  # east, west, etc.
                tmp = list(pyev.value)
                if tmp[1] != 0:
                    tmp[1] *= -1
                pyev.value = pyev.dict['value'] = tuple(tmp)
                r = (self._map_etype2kengi(pyev.type), pyev.dict)

            elif pyev.type == cst_joydown or pyev.type == cst_joyup:  # joybtdown/joybtup
                pyev.button = self.joy_bt_map[pyev.button]  # change name of the button
                setattr(pyev, 'value', int(pyev.type == cst_joydown))
                r = (self._map_etype2kengi(pyev.type), pyev.dict)

            else:
                r = (self._map_etype2kengi(pyev.type), pyev.dict)

            # modify mouse events
            if r is not None:  # some events are ignored
                if r[0] in (EngineEvTypes.Mousedown, EngineEvTypes.Mouseup, EngineEvTypes.Mousemotion):
                    r[1]['pos'] = vscreen.proj_to_vscreen(r[1]['pos'])
                    # TODO what about rel??
                self._ev_storage.append(KengiEv(r[0], **r[1]))

        return self._ev_storage
