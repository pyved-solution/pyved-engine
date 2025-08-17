# from ... import _hub
from ... import dep_linking

# TODO
# use the dynamically imported sublayer again...
# pygame = _hub.pygame

# ...meanwhile, i replace with this:
pygame = dep_linking.pygame


class Button(pygame.sprite.Sprite):

    free_bt_identifier = 77348

    def __init__(self, pos=None, size=None, label='bt_label', anchor_code=0):
        """
        :param pos:
        :param size:
        :param label:
        :param anchor_code: 0: topleft, 1: center
        """
        super().__init__()
        self.callback = None

        self.ident = Button.free_bt_identifier
        Button.free_bt_identifier += 1

        if size:
            self._w, self._h = size
        else:
            self._w, self._h = 128, 40
        if pos:
            self.pos = list(pos)
        self.image = pygame.surface.Surface((self._w, self._h))
        self.image.fill('gray')

        tmp_font = pygame.font.Font(None, 18)
        self._lbl = tmp_font.render(label, True, 'navyblue')
        self.label = label
        offsetx = self._lbl.get_width() // 2
        offsety = self._lbl.get_height() // 2
        cx, cy = self._w//2, self._h//2
        self.image.blit(self._lbl, (cx - offsetx, cy - offsety))

        pygame.draw.rect(self.image, 'navyblue', (0, 0, self._w-1, self._h-1), 2)

        # adjust position
        self.rect = self.image.get_rect()
        if not anchor_code:
            self.rect.topleft = self.pos
        else:
            self.rect.center = self.pos
        self.anchorcode = anchor_code

    def set_image(self, img):
        # KEEP THE ORG. POS!
        if not self.anchorcode:
            orgx, orgy = self.rect.topleft
        else:
            orgx, orgy = self.rect.center

        self.image = img
        self._w, self._h = img.get_size()

        self.rect = pygame.Rect(0, 0, self._w, self._h)

        # re-generate the position
        if not self.anchorcode:
            self.rect.topleft = orgx, orgy
        else:
            self.rect.center = orgx, orgy

        # debug:
        # self.image.fill('orange')
        pygame.draw.rect(self.image, 'orange', (0, 0, self._w - 1, self._h - 1), 2)
