from ... import dep_linking


pygame = dep_linking.pygame


class Trigger:
    """
    This class has been copied for better retro-compatibility with old projects
    (e.g. Brutos), but it's also used in VmSelector kartridge
    """
    class_ready_to_draw = False
    RED = None
    small_font = None
    med_font = None

    def __init__(self, pos_topleft, size):
        self.pos = pos_topleft
        self.size = size
        self.active = True
        self.visibility = True
        self.label = None
        self.spr_label = None
        self.drawing_color = pygame.Color('purple')
        sm_ft = pygame.font.Font(None, 24)
        self.med_font = sm_ft

    def set_active(self, val):
        self.active = val

    def is_active(self):
        return self.active

    def set_visible(self, val):
        assert (isinstance(val, bool))
        self.visibility = val

    def is_visible(self):
        return self.visibility

    def getSize(self):
        return self.size

    def setSize(self, new_size):
        self.size = new_size

    def setPos(self, new_pos):
        self.pos = new_pos

    def getPos(self):
        return self.pos

    def getLabel(self):
        return self.label

    def getRect(self):
        return [self.pos, self.size]

    def getCollisionBox(self):
        repr_cb = [self.pos, self.size]

        pt_topleft = repr_cb[0]

        taille_util = repr_cb[1]
        pt_botright = list(pt_topleft)
        pt_botright[0] += taille_util[0]
        pt_botright[1] += taille_util[1]

        res = list()
        res.extend(pt_topleft)
        res.extend(pt_botright)
        return res

    def setCollisionBox(self, new_cb_borders):
        # --- conversion
        taille = (
            new_cb_borders[2] - new_cb_borders[0],
            new_cb_borders[3] - new_cb_borders[1])
        pt_topleft = (new_cb_borders[0], new_cb_borders[1])
        self.setPos(pt_topleft)
        self.setSize(taille)

    def contains(self, point2d):
        if not self.active:
            return False
        tx, ty = point2d
        xbinf, ybinf, xbsup, ybsup = self.getCollisionBox()
        return (xbinf < tx < xbsup) and (ybinf < ty < ybsup)

    def setLabel(self, nouveau_label=None):
        self.label = nouveau_label
        if nouveau_label is None:
            self.spr_label = None
        else:
            self.spr_label = self.med_font.render(nouveau_label, False, self.drawing_color)

    def draw(self, screen, forced_color=None):
        if not self.visibility:  # invisible trigger
            return

        if forced_color is not None:
            self.drawing_color = forced_color
            self.setLabel(self.label)

        c1, c2, t, tt = self.getCollisionBox()
        c3 = t - c1
        c4 = tt - c2
        rect = ((c1, c2), (c3, c4))
        pygame.draw.rect(screen, self.drawing_color, rect, 1)

        if self.label is not None:
            # --- le but est dafficher ce txt au centre de la collision box
            pt_centrage = [
                (t - c1) // 2,
                (tt - c2) // 2,
            ]
            pt_centrage[0] += c1
            pt_centrage[1] += c2

            img = self.spr_label
            tmp_pt = (pt_centrage[0] - img.get_width() // 2, pt_centrage[1] - img.get_height() // 2)
            screen.blit(self.spr_label, tmp_pt)

        if forced_color is not None:
            self.drawing_color = self.RED
            self.setLabel(self.label)
