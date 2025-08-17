from ... import dep_linking


pygame = dep_linking.pygame


def create_txtblock_surf(text, ft_obj, alignment_f=0.0, debug=0, color=(0, 0, 0), bg_color=None):
    """
    goal = to produce a pygame surface
    append a pair (lbl, textRect) to render_list,one per line

    if bg_color ->None then transparent bg!!!
    
    """
    render_list = list()
    mw = mh = -1
    toth = 0
    
    for line in text.split('\n'):

        # CustomFt: crea surface, puis render...
        #text_lbl = pygame.Surface((ft_obj.width(line), 16),pygame.SRCALPHA)
        #ft_obj.render(line, text_lbl, (0,0))

        #pyg font
        text_lbl = ft_obj.render(line, False, color, bg_color)
        
        w, h = text_lbl.get_size()
        if w > mw:
            mw = w
        if h > mh:
            mh = h
        toth += h
        render_list.append(text_lbl)

    # create surf, that represents txtblock
    surf = pygame.Surface((mw, toth), pygame.SRCALPHA)
    
    # stack labels, to gen the txt block
    target_y = 0
    for lbl in render_list:
        curr_w = lbl.get_width()
        surf.blit(lbl, (alignment_f * (mw - curr_w), target_y))
        target_y += mh
    if debug:
        pygame.draw.rect(surf, 'red', ((0, 0), (mw - 1, toth - 1)), 1)
    return surf


class TextBlock(pygame.sprite.Sprite):
    ALIGN_LEFT, ALIGN_CENTER = 0, 1

    #def __init__(self, ft_name, ft_size, text='', color=(0, 0, 0), bg_color=(255, 255, 255)):
    def __init__(self, ft_obj, text='', color=(0, 0, 0), bg_color=(255, 255, 255)):
        super().__init__()
        #self.ft_obj = pygame.font.Font(ft_name, ft_size)
        self._color = color
        self._bg_color = bg_color
        self.ft_obj = ft_obj
        
        self._align = self.ALIGN_CENTER
        self._debug = 0
        self.rect = None  # no position for now
        if '' == text:
            self._text = ''
            self.image = None
        else:
            self._text = text
            self._refresh_img()

    def _refresh_img(self):
        if self.rect:  # has a position
            prev_pos = self.rect.center
        else:
            prev_pos = None

        if self._align == self.ALIGN_CENTER:
            ts = create_txtblock_surf(self._text, self.ft_obj, 0.5, self.debug, self._color)
            # ts = create_txtblock_surf(self._text, self.ft_obj, self._color, self._bg_color, 0.5, self.debug)
        else:
            ts = create_txtblock_surf(self._text, self.ft_obj, 0.0, self.debug, self._color)
            # ts = create_txtblock_surf(self._text, self.ft_obj, self._color, self._bg_color, 0.0, self.debug)
        self.image = ts
        self.rect = self.image.get_rect()
        # restore previous position
        if prev_pos:
            self.rect.center = prev_pos

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, v):
        self._debug = 1 if v else 0
        self._refresh_img()

    @property
    def text_align(self):
        return self._align

    @text_align.setter
    def text_align(self, v):
        if v in (self.ALIGN_LEFT, self.ALIGN_CENTER):
            self._align = v
            self._refresh_img()
        else:
            raise ValueError

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, val):
        self._text = val
        self._refresh_img()

    def draw(self, scr):
        if self.image:
            pos = self.rect.topleft
            scr.blit(self.image, pos)
