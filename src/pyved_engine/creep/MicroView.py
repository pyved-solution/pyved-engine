import katagames_sdk.capsule.engine_ground.conf_eng as cgmconf
from katagames_sdk.capsule.event import EventReceiver, EngineEvTypes
from katagames_sdk.capsule.pygame_provider import get_module

pyg = get_module()


class MicroView(EventReceiver):
    def __init__(self):
        super().__init__()
        fgcolor, self.bgcolor = pyg.color.Color('purple'), pyg.color.Color('antiquewhite3')

        self._font = pyg.font.Font(None, 22)

        self._label = self._font.render('CLICK HERE TO PLAY!', False, fgcolor)
        scr_w, scr_h = cgmconf.get_screen().get_size()
        self._pos = (
            (scr_w - self._label.get_width())//2,
            (scr_h - self._label.get_height())//2
        )

    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.PAINT:
            ev.screen.fill(self.bgcolor)
            ev.screen.blit(self._label, self._pos)

        elif ev.type == pyg.MOUSEBUTTONUP:
            self.pev(EngineEvTypes.CHANGESTATE, state_ident=0)
