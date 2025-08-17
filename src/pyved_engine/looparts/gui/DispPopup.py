from abc import ABCMeta, abstractmethod
from .Trigger import Trigger
from ... import dep_linking


TRIG_POPUP_GENERIC_NOP = 4
TRIG_POPUP_GENERIC_CLOSE = 5


pygame = dep_linking.pygame


class BaseGui(metaclass=ABCMeta):

    @abstractmethod
    def draw_content(self, screen):
        pass

    def lookup_firing_trigger(self, mouse_buttons, clickpos):
        """
        :param mouse_buttons: triplet de valeurs entières 0/1
        :param clickpos: couple de valeurs entières scr_x, scr_y
        :return: identifiant de trigger (int listé dans "def_triggers.py" ou None

        par défaut, il n'y a aucun déclenchement
        """
        return None


class BaseGuiDecorator(BaseGui):
    def __init__(self, decoree):
        self.decoree = decoree

    def draw_content(self, screen):
        if self.decoree is not None:
            self.decoree.draw_content(screen)
        self.draw_specific(screen)  # on dessine par dessus le dessin de la gui décorée

    def lookup_firing_trigger(self, mouse_buttons, clickpos):
        # le décorateur a la priorité p/r aux vues situées en-dessous
        ret_cette_gui = self.lookup_ft_specific(mouse_buttons, clickpos)

        # si la gui présente ne trouve rien à dire, c'est la gui décorée qui prend le relais...
        if ret_cette_gui is None:
            if self.decoree is None:
                return None
            return self.decoree.lookup_firing_trigger(mouse_buttons, clickpos)

        # sinon...
        return ret_cette_gui

    @abstractmethod
    def draw_specific(self, screen):
        pass

    @abstractmethod
    def lookup_ft_specific(self, mouse_buttons, clickpos):
        pass


class DispPopup(BaseGuiDecorator):
    """
    reste une classe abstraite : il faut indiquer quelles interactions sont possibles!
    responsabilité = dessin de la popup en elle-même, sans son contenu
    """
    AUCUN, \
        CLOSE_BUTTON, \
        OUI, \
        OK_BUTTON, \
        NON, \
        CANCEL_BUTTON, \
        OUINON, \
        OKANNULER = range(8721, 8721+8)

    RAB_W_CROIX = 32
    TITRE_PADDING_X = 18
    TITRE_PADDING_Y = 8
    LINE_SPACING_TXT = 22
    REL_CROIX_POS_NEAST_CORNER = (-18, +18)
    H_TITRE = 32
    TAILLE_BOUTONS = (100, 24)
    __EPAISSEUR_BORDS = 4

    def __init__(self, decoree, posref, titre, texte, forced_width=None, forced_height=400):
        super().__init__(decoree)

        self._presence = False

        self._idtrig_reserve_fermeture = TRIG_POPUP_GENERIC_CLOSE

        # servira plus tard au dessin cadre bleu ds lequel tout afficher
        self.blanc = (255, 255, 255)
        self.noir = 'black'
        self.bg_color = 'gray'
        self.bg_fonce = (33, 33, 33)
        self.bg_clair = (111, 111, 111)

        ft = pygame.font.Font(None, 22)
        self._font_moyenne = ft
        self._font_mono = ft
        self._font_petite = ft
        self.rect = self.pos_reference = self.pos_titre = self.pos_texte = self._img_titre = self._rect_popup \
            = self.spr_croix = self.trig_croix = None

        self._li_img_texte = list()
        self._maj_texte(texte)

        self._img_titre = None
        self._maj_titre(titre)

        self.width = forced_width if (forced_width is None) else forced_width
        self.width += self.TITRE_PADDING_X + self.RAB_W_CROIX
        self.height = forced_height

        self.rect = [posref[0], posref[1], self.width, self.height]

        self.actualize_position(posref)
        self.callbacks = {
            self.OK_BUTTON: None,
            self.CLOSE_BUTTON: None,
            self.CANCEL_BUTTON: None
        }

    def _maj_titre(self, titre):
        self._img_titre = self._font_moyenne.render(titre, True, self.blanc)

    def connect_close(self, val):
        assert isinstance(val, int)
        self._idtrig_reserve_fermeture = val

    @property
    def text(self):
        return '\n'.join(self._li_img_texte)

    @text.setter
    def text(self, v):
        self._maj_texte(v)

    def _maj_texte(self, full_txt):
        del self._li_img_texte[:]

        li_lignes = full_txt.split('\n')
        for ltexte in li_lignes:
            tmp = self._font_moyenne.render(
                ltexte,
                True,
                self.noir
            )
            self._li_img_texte.append(tmp)

    def activate(self):
        self._presence = True

    def deactivate(self):
        self._presence = False

    # def set_visibility(self, val):
    #     assert isinstance(val, bool)
    #     self._presence = val

    # --------------------------------
    #  méthodes métier
    # --------------------------------
    @staticmethod
    def check_contenance(rect, point_2d):
        xinf, xsup = rect[0], rect[0] + rect[2]
        yinf, ysup = rect[1], rect[1] + rect[3]
        if xinf <= point_2d[0] < xsup:
            if yinf <= point_2d[1] < ysup:
                return True
        return False

    def is_visible(self):
        return self._presence

    def __dessin_vignette_titre(self, screen):
        pygame.draw.rect(
            screen,
            self.noir,
            (self.rect[0], self.rect[1], self.rect[2], self.H_TITRE)
        )
        # -- fine ligne de séparation titre / contenu
        # (la ligne horizontale)
        tmp = self.pos_titre[0] - self.TITRE_PADDING_X + self.__EPAISSEUR_BORDS
        tmp_y = self.pos_titre[1] + self.H_TITRE - self.TITRE_PADDING_Y
        pygame.draw.line(
            screen,
            self.bg_clair,
            (tmp, tmp_y),
            (tmp + self.rect[2] - 2 * self.__EPAISSEUR_BORDS, tmp_y),
            2
        )
        # (la ligne verticale)
        tmp_y += 2
        pygame.draw.line(
            screen,
            self.bg_fonce,
            (tmp, tmp_y),
            (tmp + self.rect[2] - 2 * self.__EPAISSEUR_BORDS, tmp_y),
            2
        )

    def _dessin_fond_fenetre(self, screen):
        pygame.draw.rect(
            screen,
            self.bg_color,
            self.rect
        )

    def _dessin_cadre_fenetre(self, screen):
        # c'est pas optionnel ce rect! sert à dessiner les bords SOMBRES!
        pygame.draw.rect(
            screen,
            self.bg_fonce,
            self.rect,
            self.__EPAISSEUR_BORDS
        )

        # dessin deux lignes claires pr simuler ILLUMINATION venant du coin NW
        # (horizontale)
        pygame.draw.line(
            screen,
            self.bg_clair,
            (self.pos_reference[0], self.pos_reference[1]),
            (1 + self.pos_reference[0] + self.rect[2] - self.__EPAISSEUR_BORDS, self.pos_reference[1]),
            self.__EPAISSEUR_BORDS
        )

        # (verticale)
        pygame.draw.line(
            screen,
            self.bg_clair,
            (self.pos_reference[0], self.pos_reference[1] - 1),
            (self.pos_reference[0], 1 + self.pos_reference[1] + self.rect[3] - self.__EPAISSEUR_BORDS),
            self.__EPAISSEUR_BORDS
        )

    # --------------------------------
    #  utile pour redéfinitions
    # --------------------------------
    def _dessin_interieur(self, surface):
        """
        dessine spécifiquement ce qui se trouve dans le cadre de la popup
        :param surface: un rect aux bonnes dimensions pour éviter de depasser de l'affichage!
        :return:
        """
        cpt = 0
        for img_txt in self._li_img_texte:
            surface.blit(
                img_txt,
                (self.pos_texte[0], self.pos_texte[1] + cpt)
            )
            cpt += self.LINE_SPACING_TXT

    # --------------------------------
    #  Héritées de BaseGuiDecorator
    # --------------------------------
    def lookup_ft_specific(self, mouse_button, clickpos):
        if self._presence:
            if mouse_button == 1:  # bt gauche exigé pour interagir avec un popup
                if self.trig_croix.contains(clickpos):
                    cbf = self.callbacks[self.CLOSE_BUTTON]
                    if cbf:
                        cbf()
                elif DispPopup.check_contenance(self._rect_popup, clickpos):
                    return TRIG_POPUP_GENERIC_NOP

    def draw_specific(self, screen):
        if self._presence:
            self._dessin_fond_fenetre(screen)
            self.__dessin_vignette_titre(screen)
            screen.blit(
                self._img_titre,
                self.pos_titre
            )

            self._dessin_cadre_fenetre(screen)

            if self.spr_croix:
                self.spr_croix.draw(screen)
            else:
                pygame.draw.line(
                    screen,
                    self.trig_croix.drawing_color,
                    self.trig_croix.pos,
                    (self.trig_croix.pos[0]+self.trig_croix.size[0], self.trig_croix.pos[1]+self.trig_croix.size[1])
                )
                pygame.draw.line(
                    screen,
                    self.trig_croix.drawing_color,
                    (self.trig_croix.pos[0] + self.trig_croix.size[0], self.trig_croix.pos[1]),
                    (self.trig_croix.pos[0], self.trig_croix.pos[1]+self.trig_croix.size[1])
                )

            self._dessin_interieur(screen)
            self.trig_croix.draw(screen)

    def actualize_position(self, posref):
        self.rect[0], self.rect[1] = posref
        self.pos_reference = (self.rect[0], self.rect[1])
        self.pos_titre = (self.rect[0] + self.TITRE_PADDING_X, self.rect[1] + self.TITRE_PADDING_Y)
        self.pos_texte = (self.rect[0] + 16, self.rect[1] + 50)
        self._rect_popup = self.rect  # enregistré pr savoir quand on click dans la popup

        # --- croix pr quitter popup
        # TODO dessin croix via primitives (des lignes)
        # gfx_m = GfxManager.instance()
        # if not gfx_m.isLoaded(self.ID_GFX):
        #     gfx_m.loadOne(self.ID_GFX, self.FILENAME, False)
        #     gfx_m.setOriginAuto(self.ID_GFX, CODE_CENTER_ORG)

        pos_croix = (
            self.rect[0] + self.rect[2] + self.REL_CROIX_POS_NEAST_CORNER[0],
            self.rect[1] + self.REL_CROIX_POS_NEAST_CORNER[1]
        )
        # self.spr_croix = Sprite(self.ID_GFX, pos_croix)

        self.trig_croix = Trigger(
            (pos_croix[0] - 14, pos_croix[1] - 14),
            (28, 28)
        )
        self.trig_croix.set_visible(True)
