from .Trigger import Trigger

from ... import dep_linking


pygame = dep_linking.pygame


class SpriteBo:
    """
    on définit un sprite comme un élément graphique connu,
    et déjà présent en mémoire,
    dont on place une copie qq part sur lécran...
    Chaque sprite a sa position propre !
    """

    current_z_index = 0

    loaded_surfaces = {}

    @classmethod
    def link_resource(cls, gfxelt_id, filename):
        # this method is new (2022), it has been introduced so we can remove the use to GfxManager.
        cls.loaded_surfaces[gfxelt_id] = pygame.image.load(filename)

    def __init__(self, gfxelt_id, position2):
        self.pos = tuple(position2)
        self.ref_gfxelt_id = gfxelt_id
        self.z_index = self.__class__.current_z_index
        self.__class__.current_z_index += 1

    def getSurface(self):
        return self.__class__.loaded_surfaces[self.ref_gfxelt_id]  # assuming the link has been done

    def draw(self, surf):
        # self.gfx_manager.pasteGfxTo(self.ref_gfxelt_id, self.pos, surf)
        s = self.getSurface()
        surf.blit(s, self.pos)

    def getSize(self):
        # return self.gfx_manager.getSize(self.ref_gfxelt_id)
        return self.getSurface().get_size()

    def getOriginPt(self):
        # return self.gfx_manager.getOrigin(self.ref_gfxelt_id)
        return 0, 0

    def getPos(self):
        return self.pos

    def setPos(self, nouv_position2):
        self.pos = nouv_position2

    def setZIndex(self, new_val):
        self.z_index = new_val

    def getZIndex(self):
        return self.z_index

    def getGfx(self):
        return self.ref_gfxelt_id

    def setGfx(self, nouv_gfxelt_id):
        self.ref_gfxelt_id = nouv_gfxelt_id


class WidgetBo(SpriteBo):
    # classe qui utilise indirectement (via Sprite)
    # les méthodes statiques de atoms.GfxElementManage
    # pour son affichage

    def __init__(self, gfxelt_id, position2):
        super().__init__(gfxelt_id, position2)
        self.__trigger_behavior = Trigger((0, 0), (32, 32))  # position, taille
        self.hidden = False
        self.debugOff()
        self.autoResizeCollisionBox()
        self.__auto_translate_cbox()

    def setGfx(self, nouvel_id):
        super().setGfx(nouvel_id)

    def setPos(self, position2):
        super().setPos(position2)  # position sprite

        self.__auto_translate_cbox()

    def draw(self, screen):
        if not self.hidden:
            super().draw(screen)
            self.__trigger_behavior.draw(screen)

    # --- méthodes agissant sur le trigger interne
    # ----------------------------------------------
    def autoResizeCollisionBox(self):
        current_img_size = self.getSize()
        self.__trigger_behavior.setSize(current_img_size)

    def contains(self, point2):
        return self.__trigger_behavior.contains(point2)

    def __auto_translate_cbox(self):
        tmp = [0, 0]

        obj_pos = self.getPos()
        tmp[0] += obj_pos[0]
        tmp[1] += obj_pos[1]

        org = self.getOriginPt()
        tmp[0] -= org[0]
        tmp[1] -= org[1]

        self.__trigger_behavior.setPos(tmp)

    def set_active(self, val):
        self.__trigger_behavior.active = val
        if val:
            self.hidden = False
        else:
            self.hidden = True

    def is_active(self):
        return self.__trigger_behavior.active

    def debugOn(self):
        self.__trigger_behavior.set_visible(True)

    def debugOff(self):
        self.__trigger_behavior.set_visible(False)

    def getLabel(self):
        return self.__trigger_behavior.getLabel()

    def setLabel(self, label=None):
        self.__trigger_behavior.setLabel(label)

    def getCollisionBox(self):
        return self.__trigger_behavior.getCollisionBox()

    def setCollisionBox(self, li4_coord):
        self.__trigger_behavior.setCollisionBox(li4_coord)
