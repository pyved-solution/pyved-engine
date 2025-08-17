import random

from .BaseGuiElement import BaseGuiElement
from ... import dep_linking


pygame = dep_linking.pygame


class Label(BaseGuiElement):

    def __init__(self, position, txt_string, txt_size=10, color=None, anchoring=None, replacemt_ft=None):
        
        if replacemt_ft is not None:
            self.small_font = replacemt_ft
        else:
            self.small_font = pygame.font.Font(None, txt_size)

        super().__init__()
        self.set_position(position)
        self._text = txt_string
        self._txtsize = txt_size
        self._used_color = 'black'
        if color:
            self._used_color = color

        self.image = self._dim = None
        self._debug = False
        self.rebuild()

    def rebuild(self):
        self.image = self.small_font.render(self._text, False, self._used_color)
        self._dim = self.image.get_size()
        if self._parent:
            self._parent.recompute()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, v):
        self._text = v
        self.rebuild()

    def get_relative_rect(self):
        pass

    def set_relative_pos(self, position):
        pass

    def kill(self):
        pass

    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        pass

    def hover_point(self, hover_x: float, hover_y: float) -> bool:
        pass

    def proc_event(self, event) -> bool:
        pass

    def set_image(self, new_image):
        pass

    # def __init__(self, position, text, txtsize=35, color=None, anchoring=ANCHOR_LEFT, debugmode=False):
    #     self._used_text = text
    #     self._used_color = color
    #     self._txtsize = txtsize
    #     self._inner_spr = _SprLikeLabel(text, txtsize, color)
    #     super().__init__(position, self._inner_spr.rect.size, anchoring, debugmode)

    # --- define all properties ---
    @property
    def textsize(self):
        return self._txtsize

    @textsize.setter
    def textsize(self, newv):
        self._txtsize = newv
        self.rebuild()

    # @property
    # def text(self):
    #     return self._used_text
    #
    # # modifiying text => rebuild step
    # @text.setter
    # def text(self, newtext):
    #     self._used_text = newtext
    #     self.rebuild()

    @property
    def color(self):
        return self._used_color

    @color.setter
    def color(self, newval):
        self._used_color = newval
        self.rebuild()

    # --- all properties defined ---

    # def rebuild(self) -> None:
    #     """
    #     called if the spr has changed (or the color)
    #     :return:
    #     """
    #     self._inner_spr = _SprLikeLabel(self._used_text, self._txtsize, self._used_color)
    #     super().__init__(self.get_position(), self._inner_spr.rect.size, self._curr_anchor, self._debug_mode)

    def draw(self):
        # super().draw()
        self._scrref.blit(self.image, self._abs_pos)
        if self._debug:
            pygame.draw.rect(self._scrref, 'red', self.get_abs_rect(), 1)
        # self._cached_scr_ref.blit(self._inner_spr.image, topleft_coords)


if __name__ == '__main__':
    pygame.init()
    scr = pygame.display.set_mode((400, 300))
    gameover = False
    cl = pygame.time.Clock()
    central_obj = _SprLikeLabel('salut', 'steelblue')

    while not gameover:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                gameover = True
            elif ev.type == pygame.KEYDOWN:
                central_obj.color = random.choice(('antiquewhite2', 'orange', 'pink', 'yellow'))

            scr.fill('grey22')
            scr.blit(central_obj.image, central_obj.rect.topleft)
            pygame.display.update()
            cl.tick(60)

    pygame.quit()
    print('test over')
