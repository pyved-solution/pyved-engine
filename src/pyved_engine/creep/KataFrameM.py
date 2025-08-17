from katagames_sdk.capsule.event import CogObject
from katagames_sdk.capsule.event import EngineEvTypes


class KataFrameM(CogObject):
    """
    classe utilisée pr stocker temporairement login / pwd
    durant le processus de login
    Le pwd est gardé secret (pas d'affichage) mais on compte et
    on affiche correctement le nb de car
    """
    VAR_USERNAME, VAR_PWD = range(87, 87 + 2)

    def __init__(self):
        super().__init__()
        self._username_info = ''
        self._pwdplain_info = ''

        self._focusing_username = True

    def input_char(self, c):
        if self._focusing_username:
            self._username_info += c
        else:
            self._pwdplain_info += c

    # - getters
    @property
    def username(self):
        return self._username_info

    @property
    def plainpwd(self):
        return self._pwdplain_info

    def get_pwd_str(self):
        k = len(self._pwdplain_info)
        li_etoiles = '*' * k
        return ''.join(li_etoiles)

    def is_focusing_username(self):
        return self._focusing_username

    # - misc methods
    def set_focus(self, var_code):

        if var_code == self.VAR_USERNAME:
            if not self._focusing_username:
                self._focusing_username = True
                self.pev(EngineEvTypes.FOCUSCH, focusing_username=True)

        elif var_code == self.VAR_PWD:
            if self._focusing_username:
                self._focusing_username = False
                self.pev(EngineEvTypes.FOCUSCH, focusing_username=False)
        else:
            raise ValueError('unrecognized var_code')

    def toggle_focus(self):
        self._focusing_username = not self._focusing_username
        self.pev(EngineEvTypes.FOCUSCH, focusing_username=self._focusing_username)

    def suppr_lettre(self):
        if self._focusing_username:
            if len(self._username_info) > 0:
                self._username_info = self._username_info[:-1]
                self.pev(EngineEvTypes.FIELDCH, field=0, txt=self._username_info)
        else:
            if len(self._pwdplain_info) > 0:
                self._pwdplain_info = self._pwdplain_info[:-1]
                self.pev(EngineEvTypes.FIELDCH, field=1, txt=self.get_pwd_str())

    def reset_fields(self):
        self._username_info = ''
        self._pwdplain_info = ''

        self.pev(EngineEvTypes.FIELDCH, field=0, txt=self._username_info)
        self.pev(EngineEvTypes.FIELDCH, field=1, txt=self.get_pwd_str())

        self._focusing_username = True
        self.pev(EngineEvTypes.FOCUSCH, focusing_username=True)
