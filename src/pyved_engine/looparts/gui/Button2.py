from .BaseGuiElement import BaseGuiElement
from ... import dep_linking
from ...compo.vscreen import proj_to_vscreen
from ...foundation import events

pygame = dep_linking.pygame
EvListener = events.EvListener
EvManager = events.EvManager


class Button2(EvListener, BaseGuiElement):

    HIDEOUS_PURPLE = (255, 0, 255)
    DEFAULT_BG_COLOR = (75, 75, 80)
    DISABLED_COLOR = (133, 133, 133)

    def __init__(self, font, text, position_on_screen, draw_background=True, callback=None, tevent=None):
        BaseGuiElement.__init__(self)
        EvListener.__init__(self)

        # - specific attributes
        # already has self._active THIS ATTR means (display/no display & can react/cannot react) at the same time
        # we need another ATTR to say the Button has to be drawn but is disabled right now, for example!
        self._enabled = True

        if position_on_screen:
            self._abs_pos = list(position_on_screen)

        padding_value = 12  # pixels

        if draw_background:
            self.bg_color = self.DEFAULT_BG_COLOR
            self.fg_color = (255, 255, 255)
        else:
            self.bg_color = self.HIDEOUS_PURPLE
            self.fg_color = (0, 0, 0)

        # - callback func management !
        if callback and tevent:
            raise ValueError('cannot have callback & tevent set at the same time!')
        self._callback = None
        if callback:
            self._callback = callback
        elif tevent:
            def push_event():
                nonlocal tevent
                EvManager.instance().post(tevent)
            self._callback = push_event

        # - rest of the init, data etc.
        self._text = text
        self._hit = False
        if font is None:
            self.font = pygame.font.Font(None, 18)  # default
        else:
            self.font = font
        self._txt = text
        size = self.font.size(text)
        self.tmp_size = size
        # cp
        self._dim[0], self._dim[1] = size
        self.collision_rect = pygame.Rect(self._abs_pos, size).inflate(padding_value, padding_value)
        self.collision_rect.topleft = self._abs_pos
        self.image = None
        self.refresh_img()

    @property
    def label(self):
        return self._txt

    @label.setter
    def label(self, newstr):
        self._txt = newstr
        self.refresh_img()

    # - redef
    def set_active(self, newmode=True):
        bv = bool(newmode)
        super().set_active(bv)
        if bv:
            self.turn_on()
        else:
            self.turn_off()

    @property
    def enabled(self):
        return self._enabled

    def set_enabled(self, boolv=True):
        x = self._enabled
        self._enabled = bool(boolv)
        if self._enabled != x:
            self.refresh_img()  # need a re-draw, bc a disabled button has to have a different image/to look different

    def refresh_img(self):
        w, h = self.collision_rect.size
        self.image = pygame.Surface((w+8, h)).convert()
        self.image.fill(self.bg_color)

        adhoc_txt_color = self.fg_color if self._enabled else self.DISABLED_COLOR

        if self.bg_color != self.HIDEOUS_PURPLE:
            textimg = self.font.render(self._txt, True, adhoc_txt_color, self.bg_color)
        else:
            textimg = self.font.render(self._txt, False, adhoc_txt_color)

        ssdest = self.image.get_size()
        ssource = textimg.get_size()
        blit_dest = (
            (ssdest[0] - ssource[0]) // 2,
            (ssdest[1] - ssource[1]) // 2
        )
        self.image.blit(textimg, blit_dest)

        # TODO is this useful?
        # if self.bg_color == self.HIDEOUS_PURPLE:
        #     self.image.set_colorkey((self.bg_color))
        #     box_color = (190,) * 3
        #     full_rect = (0, 0, self.image.get_size()[0], self.image.get_size()[1])
        #     pygame.draw.rect(self.image, box_color, full_rect, 1)

    # pour des raisons pratiques (raccourci)
    def get_size(self):
        return self.image.get_size()

    # redefine!
    def get_dimensions(self):
        return self.image.get_size()

    def get_relative_rect(self):
        pass

    def set_relative_pos(self, position):
        pass

    def draw(self):
        if self._active:
            self._scrref.blit(self.image, self._abs_pos)
            # mega-debug
            # pygame.draw.rect(self._scrref, 'red', pygame.Rect(self._abs_pos, self.get_size()), 1)

    def kill(self):
        pass

    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        pass

    def hover_point(self, hover_x: float, hover_y: float) -> bool:
        pass

    def set_image(self, new_image):
        pass

    # - redefine!
    def set_position(self, position):
        self._abs_pos[0], self._abs_pos[1] = position
        self.collision_rect.topleft = position

    def proc_event(self, ev, source):
        if ev.type == pygame.KEYDOWN:
            self.on_keydown(ev)
        elif ev.type == pygame.MOUSEMOTION:
            self.on_mousemotion(ev)
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            self.on_mousedown(ev)
        elif ev.type == pygame.MOUSEBUTTONUP:
            self.on_mouseup(ev)

    def on_keydown(self, event):
        """
        Decides what do to with a keypress.
        special meanings have these keys:
        enter, left, right, home, end, backspace, delete
        """
        if event.type != pygame.KEYDOWN:
            print("textentry got wrong event: " + str(event))
        else:
            self.render()

    ### debug
    # if __name__=='__main__' and event.key == pygame.K_ESCAPE:
    #     events.RootEventSource.instance().stop()

    def on_mousedown(self, event):
        if self._active and self._enabled and self._callback:
            ptested = proj_to_vscreen(event.pos)
            if self.collision_rect.collidepoint(ptested):
                self._callback()

    def set_callback(self, callback):
        self._callback = callback

    def render(self):
        """

        """
        pass

    #     """
    #     Actually not needed. (only need if this module is run as a script)
    #     """
    #     # only need if this module is run as a script
    #     if __name__ == '__main__':
    #         screen = pygame.display.get_surface()
    #         screen.fill((100, 0, 0))
    #         screen.blit(self.image, self.position)
    #         pygame.display.flip()
