from ... import _hub as inj
from ...compo.vscreen import proj_to_vscreen
# from ... import event
from ...foundation.event2 import EvListener
from .BaseGuiElement import BaseGuiElement


pygame = inj.pygame


class Button2(EvListener, BaseGuiElement):

    HIDEOUS_PURPLE = (255, 0, 255)

    def __init__(self, font, text, position_on_screen, callback=None, draw_background=True):
        BaseGuiElement.__init__(self)
        EvListener.__init__(self)

        padding_value = 12  # pixels

        if draw_background:
            self.bg_color = (100, 100, 100)
            self.fg_color = (255, 255, 255)
        else:
            self.bg_color = self.HIDEOUS_PURPLE
            self.fg_color = (0, 0, 0)

        # data
        self._callback = callback
        self._text = text
        self._hit = False

        if font is None:
            self.font = pygame.font.Font(None, 18)  # default
        else:
            self.font = font
        self.txt = text

        size = self.font.size(text)
        self.tmp_size = size
        # cp
        self._dim[0], self._dim[1] = size

        # self.position = position_on_screen

        self.collision_rect = pygame.Rect(self._abs_pos, size).inflate(padding_value, padding_value)
        self.collision_rect.topleft = self._abs_pos
        self.image = None
        self.refresh_img()

    def refresh_img(self):
        self.image = pygame.Surface(self.collision_rect.size).convert()
        self.image.fill(self.bg_color)

        if self.bg_color != self.HIDEOUS_PURPLE:
            textimg = self.font.render(self.txt, True, self.fg_color, self.bg_color)
        else:
            textimg = self.font.render(self.txt, False, self.fg_color)

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
        # print( self._abs_pos)
        self._scrref.blit(self.image, self._abs_pos)
        # print('eiduateluidetlaui')

    def kill(self):
        pass

    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        pass

    def hover_point(self, hover_x: float, hover_y: float) -> bool:
        pass

    def set_image(self, new_image):
        pass

    def set_active(self, activate_mode: bool):
        pass

    # - redefine!
    def set_pos(self, position):
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
        ptested = proj_to_vscreen(event.pos)
        if self.collision_rect.collidepoint(ptested):
            if self._callback:
                self._callback()

    # def on_mouseup(self, event):
    #     pos = event.pos
    #     # print('button: mouse button up detected! x,y = {}'.format(pos))
    #
    # def on_mousemotion(self, event):
    #     pass

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

