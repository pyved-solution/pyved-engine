from .BaseGuiElement import BaseGuiElement, ANCHOR_LEFT, ANCHOR_RIGHT, ANCHOR_CENTER
from ... import dep_linking
from ...compo import vscreen
from ...abstraction import EvSystem as events


pygame = dep_linking.pygame
EngineEvTypes = events.EngineEvTypes
# pose pb en web context , parce que pygame used
# SPATIAL_INFO = Union[pygame.math.Vector2, Tuple[int, int], Tuple[float, float]]


class GenericUIElement(BaseGuiElement):
    """
    almost abstract element, all it contains is the minimal code,
    so it can be visually debugged
    """

    def set_relative_pos(self, position):
        pass

    def __init__(self, position0, dimensions0, anchoring=None, debugmode=False):
        super().__init__()

        # state/sys
        self._debug_mode = debugmode
        self._is_active = True
        self._cached_scr_ref = None

        # regular attributes
        self._dim = [-1, -1]
        self.set_dimensions(dimensions0)

        self._curr_anchor = ANCHOR_LEFT  # the default one
        if anchoring:
            self.set_anchoring(anchoring)

        self._xy_coords = [0, 0]
        self.set_position(position0)

        self._hovered_rn = False

    # ----------------------------
    #  handy, even if not made explicit by the iface
    # ----------------------------
    @property
    def x(self):
        return self.get_position()[0]

    @x.setter
    def x(self, newx):
        self.set_position((newx, self.y))

    @property
    def y(self):
        return self.get_position()[1]

    @y.setter
    def y(self, newy):
        self.set_position((self.x, newy))

    # ----------
    #  reg methods implem
    # ----------
    def rebuild(self) -> None:
        pass

    def get_position(self):
        if self._curr_anchor == ANCHOR_LEFT:
            return self._xy_coords
        elif self._curr_anchor == ANCHOR_CENTER:
            hw, hh = self._dim
            hw = int(hw / 2)
            hh = int(hh / 2)
            return self._xy_coords[0] + hw, self._xy_coords[1] + hh

    def set_position(self, position):
        # args passed are absolute!
        if self._curr_anchor == ANCHOR_LEFT:
            self._xy_coords[0], self._xy_coords[1] = position

        elif self._curr_anchor == ANCHOR_CENTER:
            hw, hh = self._dim
            hw = int(hw/2)
            hh = int(hh/2)
            self._xy_coords[0] = position[0] - hw
            self._xy_coords[1] = position[1] - hh

    def set_relative_position(self, position):
        # TODO
        raise Exception

    def get_dimensions(self):
        return self._dim

    def set_dimensions(self, dimensions):
        self._dim[0], self._dim[1] = dimensions

    def get_relative_rect(self):# -> pygame.Rect:
        pass

    def get_abs_rect(self):  # -> pygame.Rect:
        pass

    def update(self, time_delta: float):
        # GenericUIElement doesnt react
        pass

    def draw(self):
        if self._cached_scr_ref is None:
            self._cached_scr_ref = vscreen.get_screen()

        if self._debug_mode:
            pygame.draw.rect(
                self._cached_scr_ref,
                'red',
                (self._xy_coords[0]-1, self._xy_coords[1]-1, self._dim[0]+1, self._dim[1]+1),
                2  # line width
            )

    def kill(self):
        pass

    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        pass

    def hover_point(self, hover_x: float, hover_y: float) -> bool:
        pass

    def proc_event(self, event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            mx, my = vscreen.proj_to_vscreen(event.pos)
            if not self._hovered_rn:
                if self._xy_coords[0] < mx < self._xy_coords[0]+self._dim[0]:
                    if self._xy_coords[1] < my < self._xy_coords[1]+self._dim[1]:
                        self._hovered_rn = True
                        self.on_hover()

            if self._hovered_rn:
                hit = False
                if self._xy_coords[0] < mx < self._xy_coords[0]+self._dim[0]:
                    if self._xy_coords[1] < my < self._xy_coords[1]+self._dim[1]:
                        hit = True
                if not hit:
                    self._hovered_rn = False
                    self.on_unhover()
            return True
        else:
            return False

    def set_debug_mode(self, activate_mode: bool):
        self._debug_mode = activate_mode

    def set_image(self, new_image):  #: Union[pygame.surface.Surface, None]
        pass

    def set_active(self, activate_mode: bool):
        self._is_active = True

    def set_anchoring(self, anch_code):
        self._curr_anchor = anch_code

    def get_anchoring(self) -> int:
        pass

    # ---------------------------
    #  CAN be re-defined later (callbacks)
    # ---------------------------
    def on_hover(self):
        pass

    def on_unhover(self):
        pass

    def on_focus(self):
        pass

    def on_unfocus(self):
        pass


class Button(GenericUIElement):
    pass  # TODO


class AugmentedSprite(GenericUIElement):
    """
    it's like a sprite but can be clicked/hovered/focused
    """
    def __init__(self, img, anchoring=None):
        img_dim = img.get_size()
        self._inner_sprite = pygame.sprite.Sprite()
        self._inner_sprite.image = img
        self._inner_sprite.rect = img.get_rect()

        super().__init__((0, 0), img_dim, anchoring)
        self.callback = None  # can be used whenever the element is clicked!
        self.hovered = False

    @property
    def rect(self):
        return self._inner_sprite.rect

    def get_position(self):
        return self._inner_sprite.rect.topleft

    def set_position(self, pos):
        self._xy_coords[0], self._xy_coords[1] = pos
        self._inner_sprite.rect.topleft = pos

    def draw(self):
        scr = vscreen.get_screen()
        scr.blit(self._inner_sprite.image, self._inner_sprite.rect.topleft)
        if self._debug:
            pygame.draw.rect(scr, 'red', (self._inner_sprite.rect.topleft, self._inner_sprite.image.get_size()), 1)

    def proc_event(self, event) -> bool:  # event: pygame.event.Event
        if self._is_active:
            super().proc_event(event)

            if event.type == EngineEvTypes.Paint:
                self.draw()

            if event.type == pygame.MOUSEBUTTONDOWN:
                print('augmented spr knows click')
                updated_pos = vscreen.proj_to_vscreen(event.pos)

                if self._inner_sprite.rect.collidepoint(updated_pos):  # hit
                    print('HIT on augmented sprite detected...')
                    if self.callback is not None:
                        self.callback(event.button)
            return True
        else:
            return False



class _SprLikeLabel(pygame.sprite.Sprite):
    # TODO make it a UIelement

    def __init__(self, txt, txtsize, color=None):
        self._font = pygame.font.Font(None, txtsize)

        super().__init__()

        self._txt = txt

        self._color = [0, 0, 0]
        if color:
            try:
                self._color[0], self._color[1], self._color[2] = color.r, color.g, color.b
            except (ValueError, AttributeError):
                # force conversion to color
                c = pygame.color.Color(color)
                self._color[0], self._color[1], self._color[2] = c.r, c.g, c.b
        # init image & rect, as well!
        self.color = self._color

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.image = self._font.render(self._txt, False, value)
        self.rect = self.image.get_rect()
