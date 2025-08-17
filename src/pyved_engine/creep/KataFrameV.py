import time

import katagames_sdk.capsule.gui as gui
from katagames_sdk.capsule.bioslike.KataFrameM import KataFrameM
from katagames_sdk.capsule.event import EngineEvTypes, EventReceiver, EventManager, CgmEvent
from katagames_sdk.capsule.pygame_provider import get_module

pygame = get_module()


BIOS_FG_COL_DESC = 'purple'
BIOS_BG_COL_DESC = 'antiquewhite3'


class KataFrameV(EventReceiver):
    """
    affiche écran intermédiaire permettant la SAISIE des IDENT.
    """

    TEXT_INPUT_SIZE = 160
    ERR_MSG_DELAY = 2.5  # sec
    POS_BT_BROWSER = (385/2, 215/2)
    TAQ_XALIGN_BOX = 150
    TAQ_XALIGN_LABELS = 50
    VOFFSET = 24
    POS_BT_CONFIRM = (TAQ_XALIGN_LABELS, 199)
    POS_BT_CANCEL = (TAQ_XALIGN_LABELS, 199+30)

    # ------------------
    #  positions des labels
    # TODO ramener depuis extérieur classe

    def __init__(self, ref_mod):
        super().__init__()
        fgcolor, bgcolor = pygame.color.Color(BIOS_FG_COL_DESC), pygame.color.Color(BIOS_BG_COL_DESC)

        self.bgcolor = bgcolor
        self.fgcolor = fgcolor

        self._ref_mod = ref_mod

        self._font = pygame.font.Font(None, 22)
        self._buttons = list()
        self._crea_boutons()

        # self.red_color = glvars.colors['c_cherokee']
        self._fin_aff_flottant = None

        gui.Etiquette.set_font(self._font)

        init_yv = 22
        y_lig1 = init_yv+4*self.VOFFSET
        y_lig2 = init_yv+5*self.VOFFSET
        self._etiquettes = [
            gui.Etiquette('KATA.GAMES auth procedure', (self.TAQ_XALIGN_LABELS, init_yv), self.fgcolor),
            gui.Etiquette('if you need a new account, please', (self.TAQ_XALIGN_LABELS, init_yv+1*self.VOFFSET), self.fgcolor),
            gui.Etiquette('use our website https://kata.games', (self.TAQ_XALIGN_LABELS, init_yv+2*self.VOFFSET), self.fgcolor),
            gui.Etiquette('username', (self.TAQ_XALIGN_LABELS, y_lig1), self.fgcolor),
            gui.Etiquette('password', (self.TAQ_XALIGN_LABELS, y_lig2), self.fgcolor)
        ]

        self._err_etiquette = gui.Etiquette(
            'ERR: server does not recognize this account', (self.TAQ_XALIGN_LABELS, init_yv+3*self.VOFFSET), (255, 0, 0)
        )
        self.saisie_txt1 = gui.TextInput('>', self._font, KataFrameV.nop, (self.TAQ_XALIGN_BOX, y_lig1), self.TEXT_INPUT_SIZE)
        self.saisie_txt2 = gui.TextInput('>', self._font, KataFrameV.nop, (self.TAQ_XALIGN_BOX, y_lig2), self.TEXT_INPUT_SIZE)
        self.saisie_txt2.pwd_field = True

    @staticmethod
    def confirm_routine():
        # TODO déclencher interrogation serveur
        # TODO exporter trucs vers le contrôleur, c'est lui qui va popstate
        ev = CgmEvent(EngineEvTypes.DOAUTH)
        EventManager.instance().post(ev)

    @staticmethod
    def cancel_routine():
        ev = CgmEvent(EngineEvTypes.POPSTATE)  # state_ident=GameStates.IntroJeu)
        EventManager.instance().post(ev)

    @staticmethod
    def nop(txt):
        pass

    def _crea_boutons(self):
        txt = 'connection'
        bt = gui.Button(self._font, txt, self.POS_BT_CONFIRM, KataFrameV.confirm_routine)
        self._buttons.append(bt)

        txt = 'abort'
        bt = gui.Button(self._font, txt, self.POS_BT_CANCEL, KataFrameV.cancel_routine)
        self._buttons.append(bt)

    # - activation / désactivation impacte boutons également
    def turn_on(self, prio=None):
        super().turn_on()

        for bt in self._buttons:
            bt.turn_on()

        if self._ref_mod.is_focusing_username():
            self.saisie_txt1.focus()
            self.saisie_txt1.turn_on()
        else:
            self.saisie_txt2.focus()
            self.saisie_txt2.turn_on()

    def turn_off(self):
        super().turn_off()

        for bt in self._buttons:
            bt.turn_off()

        if self._ref_mod.is_focusing_username():
            self.saisie_txt1.no_focus()
            self.saisie_txt1.turn_off()
        else:
            self.saisie_txt2.no_focus()
            self.saisie_txt2.turn_off()

    # ########################################################
    #  proc_event
    # ########################################################
    def proc_event(self, ev, source):
        if ev.type == EngineEvTypes.PAINT:
            self._paint(ev.screen)

        # GUI controls
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            if self.saisie_txt1.contains(ev.pos):
                self._ref_mod.set_focus(KataFrameM.VAR_USERNAME)
            elif self.saisie_txt2.contains(ev.pos):
                self._ref_mod.set_focus(KataFrameM.VAR_PWD)

        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_TAB:
                self._ref_mod.toggle_focus()
            elif ev.key == pygame.K_RETURN or ev.key == pygame.K_KP_ENTER:
                KataFrameV.confirm_routine()  # view > ctrl comm.

        # updating view (mod > view comm.)
        elif ev.type == EngineEvTypes.FIELDCH:
            if ev.field:  # pwd
                if ev.txt == '':
                    self.saisie_txt2.move_caret('home')
                    while self.saisie_txt2.get_disp_text() != '':
                        self.saisie_txt2.delete_char()
                    self.saisie_txt2.render_field()
            else:
                if ev.txt == '':
                    self.saisie_txt1.move_caret('home')
                    while self.saisie_txt1.get_disp_text() != '':
                        self.saisie_txt1.delete_char()
                    self.saisie_txt1.render_field()

        elif ev.type == EngineEvTypes.FOCUSCH:
            if ev.focusing_username:
                self._gui_focus_username()
            else:
                self._gui_focus_pwd()

    # - métier
    def _gui_focus_username(self):
        if self.saisie_txt2.has_focus():
            self.saisie_txt2.no_focus()
            self.saisie_txt2.turn_off()

            self.saisie_txt1.focus()
            self.saisie_txt1.turn_on()

    def _gui_focus_pwd(self):
        if self.saisie_txt1.has_focus():
            self.saisie_txt1.no_focus()
            self.saisie_txt1.turn_off()

            self.saisie_txt2.focus()
            self.saisie_txt2.turn_on()

    def _paint(self, screen):
        screen.fill(self.bgcolor)
        for e in self._etiquettes:
            screen.blit(e.img, e.pos)

        # - dessin boutons & widgets
        for b in self._buttons:
            screen.blit(b.image, b.position)
        screen.blit(self.saisie_txt1.image, self.saisie_txt1.position)
        screen.blit(self.saisie_txt2.image, self.saisie_txt2.position)

        if self._fin_aff_flottant is not None:
            t = time.time()
            if t > self._fin_aff_flottant:
                self._fin_aff_flottant = None
            else:
                screen.blit(self._err_etiquette.img, self._err_etiquette.pos)

    def sig_bad_auth(self):  # triggered externally by a ctrl class
        self._fin_aff_flottant = time.time() + self.ERR_MSG_DELAY
