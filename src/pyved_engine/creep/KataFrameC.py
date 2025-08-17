import katagames_sdk.api as katapi
import katagames_sdk.capsule.engine_ground.conf_eng as cgmconf
from katagames_sdk.capsule.pygame_provider import get_module
from katagames_sdk.engine import EventReceiver, EngineEvTypes


pygame = get_module()


class KataFrameC(EventReceiver):

    def __init__(self, ref_mod, ref_view):
        super().__init__()
        self.ref_mod = ref_mod
        self.ref_view = ref_view
        self.glvars_module = None

    def proc_event(self, ev, source):

        if ev.type == EngineEvTypes.DOAUTH:
            self._handle_auth()

        elif ev.type == pygame.KEYDOWN:
            self._handle_keypress(ev)

        elif ev.type == pygame.QUIT:
            self.pev(EngineEvTypes.POPSTATE)

    def _handle_auth(self):
        login_feedback = katapi.try_auth_server(self.ref_mod.username, self.ref_mod.plainpwd)

        if login_feedback:
            username, acc_id = self.ref_mod.username, int(login_feedback)
            self.glvars_module.username = username
            self.glvars_module.acc_id = acc_id

            if cgmconf.runs_in_web():
                print('commit to session_storage ->ye')
                katapi.save_to_local_session(username, acc_id)
            self.pev(EngineEvTypes.CHANGESTATE, state_ident=0)

        else:
            self.ref_mod.reset_fields()
            # gestion refus -> affiche un message erreur
            self.ref_view.sig_bad_auth()

    def _handle_keypress(self, ev):
        if ev.key == pygame.K_RETURN or ev.key == pygame.K_KP_ENTER:
            pass

        elif ev.key == pygame.K_ESCAPE:
            self.pev(EngineEvTypes.POPSTATE)

        elif ev.key == pygame.K_TAB:
            return  # sert à ignorer caractères TAB ds la saisie

        elif ev.key == pygame.K_BACKSPACE:
            self.ref_mod.suppr_lettre()

        else:
            self.ref_mod.input_char(ev.unicode)  # register the key
