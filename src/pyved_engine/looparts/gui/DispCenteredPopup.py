from .DispPopup import DispPopup
from .Trigger import Trigger
from ... import dep_linking
from ... import pe_vars


pygame = dep_linking.pygame


class DispCenteredPopup(DispPopup):

    def __init__(self, decoree, titre, txt, wanted_buttons=DispPopup.AUCUN, ppsize=(294, 140)):
        super().__init__(
            decoree, (0, 0), titre, txt, ppsize[0], ppsize[1]
        )  # der. => forcer hauteur fenetre

        scrw, scrh = vars.screen.get_size()
        self.actualize_position((
            int((scrw / 2) - (self.width / 2)),
            int((scrh / 2) - (self.height / 2))
        ))

        self.ft = pygame.font.Font(None, 18)  # glvars.gl_fonts['pxled_med_font_big']  # police par défaut
        self.white = (255, 255, 255)
        self.gris = (66, 66, 66)  # glvars.gl_colors['gris_fonce']
        self.txt_img = self.ft.render(txt, True, self.white)

        self.xt = scrw // 2 - self.txt_img.get_size()[0] // 2
        self.yt = scrh // 2 - self.txt_img.get_size()[1] // 2

        self.xoui = self.xt - 25
        self.youi = self.yt + (ppsize[1] // 2) - 25

        self.xnon = self.xt + self.width - self.TAILLE_BOUTONS[0]
        self.ynon = self.youi

        self.bouton_oui_ok = Trigger((self.xoui, self.youi), self.TAILLE_BOUTONS)
        self.bouton_oui_ok.set_visible(False)
        self.bouton_non_annuler = Trigger((self.xnon, self.ynon), self.TAILLE_BOUTONS)
        self.bouton_non_annuler.set_visible(False)

        self._construction_boutons_ona(wanted_buttons)

        self._idtrig_reserve_ok_oui = None

    def is_active(self):
        return self._presence

    def connect_ok(self, trigid):
        assert isinstance(trigid, int)
        self._idtrig_reserve_ok_oui = trigid

    def _construction_boutons_ona(self, boutons):
        # print("Boutons: {0}".format(boutons))
        if boutons in (self.OUI, self.OUINON):
            self.bouton_oui_ok.setLabel("Oui")
            self.bouton_oui_ok.set_visible(True)

        if boutons in (self.OK_BUTTON, self.OKANNULER):
            print('ajout bt OK ..............')
            self.bouton_oui_ok.setLabel("Ok")
            self.bouton_oui_ok.set_visible(True)

        if boutons in (self.NON, self.OUINON):
            self.bouton_non_annuler.setLabel("Non")
            self.bouton_non_annuler.set_visible(True)

        if boutons in (self.CANCEL_BUTTON, self.OKANNULER):
            self.bouton_non_annuler.setLabel("Annuler")
            self.bouton_non_annuler.set_visible(True)

    def draw_specific(self, screen):
        if self._presence:
            super().draw_specific(screen)
            self._dessin_boutons_ona(screen)

    def _dessin_boutons_ona(self, screen):

        for trig in (self.bouton_oui_ok, self.bouton_non_annuler):
            if trig.is_visible():
                tmp_x = trig.getPos()[0]
                tmp_y = trig.getPos()[1]
                size_x = super().TAILLE_BOUTONS[0]
                size_y = super().TAILLE_BOUTONS[1]

                rect = (
                    tmp_x,
                    tmp_y,
                    size_x,
                    size_y
                )
                pygame.draw.rect(
                    screen,
                    self.gris,
                    rect
                )
                pygame.draw.line(
                    screen,
                    self.bg_clair,
                    (tmp_x, tmp_y + size_y),
                    (tmp_x + size_x, tmp_y + size_y),
                    2
                )

                trig.draw(screen)

    def get_absolute_position(self, pos):
        # Retourne un couple de coordonnées correspondant à la position absolue d'un composant dans l'écran
        # par rapport à sa position relative au coin supérieur gauche de son conteneur
        return [pos[0] + self.x, pos[1] + self.y]

    def lookup_ft_specific(self, mouse_buttons, clickpos):
        clickpos = clickpos  # vscreen.proj_to_vscreen(clickpos)

        print(mouse_buttons, clickpos)

        if not self._presence:
            print('no presence to catch mouseclick')
            return

        if self.bouton_oui_ok.contains(clickpos):
            cbf = self.callbacks[self.OK_BUTTON]
            if cbf:
                cbf()
            return True

        if self.bouton_non_annuler.contains(clickpos):
            cbf = self.callbacks[self.CANCEL_BUTTON]
            if cbf:
                cbf()
            return True

        tmp = super().lookup_ft_specific(mouse_buttons, clickpos)
        return tmp
