import time

from .. import _hub
from ..compo import vscreen
from ..utils import func


text = func.drawtext


class Button:
    def __init__(self, x=0, y=0, w=100, h=50, label='Button', action=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.action = action
        self.label = label
        self.text = text(self.label, 40, aliased=True)
        self.active_color = (204, 122, 68)
        self.inactive_color = (182, 122, 87)
        self.rect = _hub.pygame.Rect(self.x, self.y, self.w, self.h)
        self.is_active = False

    def update(self, events):
        mx, my = vscreen.proj_to_vscreen(_hub.pygame.mouse.get_pos())

        if self.rect.collidepoint(mx, my):
            self.is_active = True
        else:
            self.is_active = False
        for e in events:
            if e.type == _hub.pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if self.is_active:
                        if self.action is not None:
                            self.action()

    def draw(self, surf):
        color = self.active_color if self.is_active else self.inactive_color
        _hub.pygame.draw.rect(surf, color, (self.x, self.y, self.w, self.h), border_radius=5)
        surf.blit(self.text, self.text.get_rect(center=self.rect.center))


class Label:
    def __init__(self, x=0, y=0, w=100, h=50, label='Label'):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = label
        self.text = text(self.label, size=25, aliased=True)
        self.color = (182, 122, 87)
        self.rect = _hub.pygame.Rect(self.x, self.y, self.w, self.h)
        self.is_active = False

    def update(self, events):
        pass

    def draw(self, surf):
        _hub.pygame.draw.rect(surf, self.color, (self.x, self.y, self.w, self.h))
        surf.blit(self.text, self.text.get_rect(center=self.rect.center))


class InputBox:
    def __init__(self, x=0, y=0, w=100, h=50, default='Type Here', initial_string='', label='none', extendable=True, numeric_only=False):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = _hub.pygame.Rect(self.x, self.y, self.w, self.h)
        self.numeric_only = numeric_only
        self.active_color = (204, 122, 68)
        self.inactive_color = (182, 122, 87)
        self.label = label
        self.default = default
        self.extendable = extendable
        self.is_active = False
        self.is_hovered = False
        self.text = initial_string
        self.allowed_input = 'abcdefghijklmnopqrstuvwxyz1234567890' if not self.numeric_only else '1234567890'
        self.cursor_visible = True
        self.cursor_blink_timer = time.time()

    def update(self, events):
        pygame = _hub.pygame
        mx, my = vscreen.proj_to_vscreen(pygame.mouse.get_pos())
        if self.rect.collidepoint(mx, my):
            self.is_hovered = True
        else:
            self.is_hovered = False
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if self.is_hovered:
                        self.is_active = True
                    else:
                        self.is_active = False
            if e.type == pygame.KEYDOWN:
                if self.is_active:
                    if e.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    if not len(self.text) > self.w // 15 - 3:
                        if e.key == pygame.K_SPACE:
                            self.text += ' '
                        # elif e.key != pygame.KMOD_SHIFT and chr(e.key) in self.allowed_input:
                        #     self.text += chr(e.key).upper()
            if e.type == pygame.TEXTINPUT:
                if self.is_active:
                    if e.text.lower() in self.allowed_input:
                        if not len(self.text) > self.w // 15 - 3:
                            self.text += e.text

    def draw(self, surf):
        color = self.active_color if self.is_hovered or self.is_active else self.inactive_color
        if self.is_active:
            display_text = self.text
        else:
            display_text = self.text if self.text != '' else self.default
        if self.is_active:
            if time.time() - self.cursor_blink_timer > 0.5:
                self.cursor_blink_timer = time.time()
                self.cursor_visible = not self.cursor_visible
            if self.cursor_visible:
                display_text += '_'
            else:
                display_text += ' '
        t = text(display_text, 25, aliased=True)
        _hub.pygame.draw.rect(surf, color, self.rect)
        surf.blit(t, t.get_rect(center=self.rect.center))
