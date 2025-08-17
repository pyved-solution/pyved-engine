import math

from .BaseGuiElement import BaseGuiElement
from ... import dep_linking


pygame = dep_linking.pygame


class WidgetContainer(BaseGuiElement):
    LTR = 1
    EXPAND = 2
    FLOW = 3

    def __init__(self, pos, size, layout_type, widget_list=None, spacing=0, vspacing=0):
        super().__init__()
        assert isinstance(layout_type, int)

        self._active = False

        self.set_position(pos)
        self.set_dimensions(size)
        self.content = list()
        if widget_list is not None:
            if isinstance(widget_list, dict):
                self.dictmode = 1
                self.cpdict = dict(widget_list)
                self.content.extend(widget_list.values())
            else:
                self.dictmode = 0
                self.content.extend(widget_list)

        for elt in self.content:
            elt._parent = self
        # reposition elements that belong to this(self) container
        self.spacing = spacing
        self.vspacing = vspacing
        self.layout_type = layout_type
        self.recompute()

    # -- redef!
    def set_active(self, activate_mode=True):
        if activate_mode:
            print('xxx Activation de l\'element', self)
        else:
            print(self, ' est désactivé!')

        super().set_active(activate_mode)

        for e in self.content:
            e.set_active(activate_mode)

    def recompute(self):
        print(self.get_abs_rect(), 'recomputing positions...')
        print('layout?', self.layout_type, '//', self.LTR,  self.EXPAND, self.FLOW,)
        print(len(self.content), 'elements')

        # adjust positions automatically!
        if self.layout_type == self.LTR:
            c_pos = [0, 0]
            for w in self.content:
                w.set_position(
                    (self._abs_pos[0] + c_pos[0], self._abs_pos[1])
                )
                c_pos[0] += w.get_dimensions()[0] + self.spacing

        # ----------------------
        # the 'expand' layout
        elif self.layout_type == self.EXPAND:
            px, py, bsupx, bsupy = self.get_abs_rect()

            delta = 0  # use (bsupy//2), if u want vertical align:center of the anchor point(topleft)
            c_pos = [px+1, py+delta]
            s = 0
            for w in self.content:
                s += w.get_dimensions()[0]
            blank_total_space = bsupx - s
            auto_spacing = math.floor(blank_total_space / (len(self.content)-1))

            for w in self.content:
                w.set_position(c_pos)
                c_pos[0] += w.get_dimensions()[0]+auto_spacing

        # ----------------------
        # the 'flow' layout
        elif self.layout_type == self.FLOW:
            basex, basey, container_w, container_h = self.get_abs_rect()
            curr_p = [basex, basey]

            prevwidget_w, prevwidget_h = 0, 0
            k = 0
            for w in self.content:
                if k:
                    curr_p[0] += (prevwidget_w + self.spacing)
                if w.get_dimensions()[0]+curr_p[0] > container_w+basex:
                    curr_p[0] = basex
                    curr_p[1] += prevwidget_h + self.vspacing

                w.set_position(curr_p)
                prevwidget_w, prevwidget_h = w.get_dimensions()
                k += 1

    # redef!
    def set_debug_flag(self, v=True):
        super().set_debug_flag(v)
        for elt in self.content:
            elt.set_debug_flag(v)

    def update_pos_from_child(self, a, b):
        pass

    def __getitem__(self, item):
        if not self.dictmode:
            raise RuntimeError
        return self.cpdict[item]

    def get_relative_rect(self):
        pass

    def set_relative_pos(self, position):
        pass

    def draw(self):
        if self._active:
            if self._debug:
                pygame.draw.rect(self._scrref, 'red', self.get_abs_rect(), 1)
            for elt in self.content:
                elt.draw()

    def kill(self):
        pass

    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        pass

    def hover_point(self, hover_x: float, hover_y: float) -> bool:
        pass

    def proc_event(self, event) -> bool:
        pass

    def on_unfocus(self):
        pass

    def set_image(self, new_image):
        pass

