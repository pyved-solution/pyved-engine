
"""
TODO support .json, uncompressed files
"""
from ... import _hub as inj
pygame = inj.pygame


class SpriteLayer(pygame.sprite.AbstractGroup):
    def __init__(self):
        super(SpriteLayer, self).__init__()
        self.visible = True

    def set_view(self, x, y, w, h, viewport_ox=0, viewport_oy=0):
        self.view_x, self.view_y = x, y
        self.view_w, self.view_h = w, h
        x -= viewport_ox
        y -= viewport_oy
        self.dx = viewport_ox
        self.dy = viewport_oy
        self.position = (x, y)

    def draw(self, screen):
        ox, oy = self.position
        w, h = self.view_w, self.view_h

        for sprite in self.sprites():
            sx, sy = sprite.rect.topleft
            # Only the sprite's defined width and height will be drawn
            area = pygame.Rect((0, 0),
                               (sprite.rect.width,
                                sprite.rect.height))
            screen.blit(sprite.image, (sx - ox, sy - oy), area)


class Viewport(pygame.Rect):
    """
    viewport: based upont pygame.Rect (pygame obj. for storing rectangular coordinates)

    can draw tilemaps, constrained by viewport origin and dimensions

    attributes:
    fx, fy - viewport focus point
    view_w, view_h - viewport size
    view_x, view_y - viewport offset (origin)
    """
    _old_focus = None

    def __init__(self,  tilemap_ref, origin, size, **kwargs):
        super().__init__(origin, size)
        self._tm = tilemap_ref  # Tilemap instance

        self.fx, self.fy = 0, 0  # viewport focus point
        self.view_w, self.view_h = size  # viewport size
        self.view_x, self.view_y = origin  # viewport offset

        # rn the followin line is very important as it is responible for
        # init. Layer draw process (forcing .set_view(...) call)
        # and to set offset properly!
        self.force_focus(*origin)
        # debug: print('force_focus: ', origin[0], origin[1])

        # this is like a temp storage
        self.childs_ox, self.childs_oy = None, None

        # wtf? how is this useful
        self.restricted_fx, self.restricted_fy = None, None

        for ckey, val in kwargs.items():
            setattr(self, ckey, val)

    def set_focus(self, fx, fy, force=False):
        """
        Determine the viewport based on a desired focus pixel in the
        Layer space (fx, fy) and honoring any bounding restrictions of
        child layers.

        The focus will always be shifted to ensure no child layers display
        out-of-bounds data, as defined by their dimensions px_width and px_height.
        """
        # -debug
        # print('set_focus CALL. Args= ', fx, fy)

        # The result is that all chilren will have their viewport set, defining
        # which of their pixels should be visible.
        fx, fy = int(fx), int(fy)
        self.fx, self.fy = fx, fy

        a = (fx, fy)

        # check for NOOP (same arg passed in)
        if not force and self._old_focus == a:
            # noop
            return
        self._old_focus = a

        # get our viewport information, scaled as appropriate
        w = int(self.view_w)
        h = int(self.view_h)
        w2, h2 = w // 2, h // 2

        totwidth, totheight = self._tm.pix_width, self._tm.pix_height
        if totwidth <= w:
            # this branch for centered view and no view jump when
            # crossing the center; both when world width <= view width
            restricted_fx = totwidth / 2
        else:
            if (fx - w2) < 0:
                restricted_fx = w2  # hit minimum X extent
            elif (fx + w2) > totwidth:
                restricted_fx = totwidth - w2  # hit maximum X extent
            else:
                restricted_fx = fx

        if self._tm.pix_height <= h:
            # this branch for centered view and no view jump when
            # crossing the center; both when world height <= view height
            restricted_fy = totheight / 2
        else:
            if (fy - h2) < 0:
                restricted_fy = h2  # hit minimum Y extent
            elif (fy + h2) > totheight:
                restricted_fy = totheight - h2  # hit maximum Y extent
            else:
                restricted_fy = fy

        # ... and this is our focus point, center of screen
        self.restricted_fx = int(restricted_fx)
        self.restricted_fy = int(restricted_fy)

        # determine child view bounds to match that focus point
        x, y = int(restricted_fx - w2), int(restricted_fy - h2)
        self._match_focus_pt(x, y, w, h)

    def force_focus(self, fx, fy):
        """
        Force the manager to focus on a point,
        regardless of any managed layer visible boundaries.
        """

        # This calculation takes into account the scaling of this Layer (and
        # therefore also its children).
        # The result is that all chilren will have their viewport set, defining
        # which of their pixels should be visible.
        self.fx, self.fy = list(map(int, (fx, fy)))

        # self.fx, self.fy = fx, fy

        # get our view size
        w = int(self.view_w)
        h = int(self.view_h)
        w2, h2 = w // 2, h // 2

        # bottom-left corner of the viewport
        x, y = fx - w2, fy - h2
        self._match_focus_pt(x, y, w, h)

    def _match_focus_pt(self, x, y, dimw, dimh):
        self.x = x  # self.x is a super(), that is Rect-defined attribute
        self.y = y  # self.y is a super(), that is Rect-defined attribute

        # change offsets, n update all layers view
        self.childs_ox = x - self.view_x
        self.childs_oy = y - self.view_y
        for layer in self._tm.layers:
            layer.set_view(x, y, dimw, dimh, self.view_x, self.view_y)

    def draw(self, screen):
        for layer in self._tm.layers:
            if layer.visible:
                layer.draw(screen)

    # - utils
    def pixel_from_screen(self, x, y):
        # look up the Layer-space pixel matching the screen-space pixel.
        vx, vy = self.childs_ox, self.childs_oy
        return int(vx + x), int(vy + y)

    def pixel_to_screen(self, x, y):
        # look up the screen-space pixel matching the Layer-space pixel
        screen_x = x - self.childs_ox
        screen_y = y - self.childs_oy
        return int(screen_x), int(screen_y)

    def index_at(self, x, y):
        # return the map index at the (screen-space) pixel position.
        sx, sy = self.pixel_from_screen(x, y)
        return int(sx // self._tm.tile_width), int(sy // self._tm.tile_height)
