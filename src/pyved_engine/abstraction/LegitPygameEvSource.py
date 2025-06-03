from ..ifaces.DeepEvSource import DeepEvSource
from ..concr_engin.pe_vars import KengiEv


class LegitPygameEvSource(DeepEvSource):

    def __init__(self, **kwargs):  # Careful! Since DeepEvSource is used as parameter for CustomizableCode, make use of kwargs is a better practice
        ev_types_atlas = kwargs['ev_types_atlas']

        import pygame as _genuine_pyg

        self.joy_bt_map = {
            0: 'A',
            1: 'B',
            2: 'X',
            3: 'Y',
            4: 'lB',
            5: 'rB',
            6: 'Back',
            7: 'Start'
        }
        self.dpad_mapping = {
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

        # TODO fix code temporaire qui est là pr améliorer (code layout) du moteur
        # injector = _hub.get_injector()
        # injector.set('pygame', _genuine_pyg)

        self._pygame_mod = _genuine_pyg
        self.debug_mode = False

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

    def upload_raw_events(self, buffer_li):
        buffer_li.extend(self._pygame_mod.event.get())
