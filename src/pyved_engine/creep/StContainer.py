import sys
import traceback
from katagames_sdk.capsule.engine_ground.BaseGameState import BaseGameState
from katagames_sdk.capsule.bioslike.MicroView import MicroView
from katagames_sdk.capsule.engine_ground.util import underscore_format
from katagames_sdk.capsule.struct.Singleton import Singleton

# import glvars
# import katagames_sdk.engine as kataen
# from app.title_screen.MenuCtrl import MenuCtrl
# from app.title_screen.TitleModel import TitleModel
# from app.title_screen.TitleView import TitleView
# pygame = kataen.import_pygame()

# import glvars
# import katagames_sdk.api as katapi
# import katagames_sdk.engine as kataen
# from app.login.LoginCtrl import LoginCtrl
# from app.login.LoginMod import LoginMod
# from app.login.LoginView import LoginView
# from ev_types import MyEvTypes
# from katagames_sdk.engine import EventReceiver, EngineEvTypes
# pygame = kataen.import_pygame()
from katagames_sdk.capsule.cli_side_api import has_pre_auth, get_credentials


class KataFrameState(BaseGameState):

    def __init__(self, gs_ident, name):
        super().__init__(gs_ident, name)
        self.m = self.v = self.c = None
        self.v2 = None
        self.glvars_module = None

    def enter(self):
        print('BIOS in')
        from katagames_sdk.capsule.bioslike.KataFrameM import KataFrameM
        from katagames_sdk.capsule.bioslike.KataFrameV import KataFrameV
        from katagames_sdk.capsule.bioslike.KataFrameC import KataFrameC

        self.m = KataFrameM()

        # the state can change right away, if login info is found...
        if not has_pre_auth():
            self.v = KataFrameV(self.m)
        else:
            username, player_id = get_credentials()
            print('fetched from session storage: {}, {}'.format(username, player_id))
            self.glvars_module.username = username
            self.glvars_module.acc_id = player_id
            self.v = MicroView()

        self.c = KataFrameC(self.m, self.v)
        self.c.glvars_module = self.glvars_module

        self.resume()

    def release(self):
        print('BIOS out')
        self.pause()
        self.m = self.v = self.c = None

    def pause(self):
        if self.v:
            self.v.turn_off()
        else:
            self.v2.turn_off()
        self.c.turn_off()

    def resume(self):
        self.v.turn_on()
        self.c.turn_on()


@Singleton
class StContainer:
    """
    contient toutes les instances de classes qui dérivent de BaseGameState
    """
    def __init__(self):
        self.__setup_done = False
        self.assoc_id_state_obj = dict()

    def hack_bios_state(self, gs_obj):
        self.assoc_id_state_obj[-1] = gs_obj

    def setup(self, enum_game_states, pymodule, stmapping):
        self.__setup_done = True

        gs_obj = KataFrameState(-1, 'KataFrame')
        gs_obj.glvars_module = pymodule
        self.hack_bios_state(gs_obj)

        # -- initialisation d'après ce qu'on recoit comme enumeration...
        for id_choisi, nom_etat in enum_game_states.inv_map.items():
            nom_cl = nom_etat + 'State'

            if stmapping:  # but = charger en mémoire la classe
                adhoc_cls = stmapping[nom_cl]  # class has been provided

                obj = adhoc_cls(id_choisi, nom_etat)
                self.assoc_id_state_obj[id_choisi] = obj
            else:
                pymodule_name = underscore_format(nom_etat)
                pythonpath = 'app.{}.state'.format(pymodule_name)
                print('StContainer is loading a new game state...')
                try:
                    pymodule = __import__(pythonpath, fromlist=[nom_cl])
                    adhoc_cls = getattr(pymodule, nom_cl)  # class has been retrieved -> ok

                    obj = adhoc_cls(id_choisi, nom_etat)
                    self.assoc_id_state_obj[id_choisi] = obj

                except ImportError as exc:
                    print('adhoc module name(conv. to underscore format)={}'.format(pymodule_name))
                    print('full path for finding class={}'.format(pythonpath))
                    print('target class={}'.format(nom_cl))
                    print('WEB CONTEXT WARNING: make sure you dont have a file named app.py in your project!')
                    sys.stderr.write("Error: failed to import class {} (info= {})\n".format(nom_cl, exc))
                    traceback.print_last()

    def retrieve(self, identifiant):
        """
        :param identifiant: peut-être aussi bien le code (int) que le nom de classe dédiée (e.g. PlayState)
        :return: instance de BaseGameState
        """

        # construction par nom ou identifiant entier
        # TODO rétablir recherche par nom et non par code...

        # if isinstance(identifiant, str):
        #     gamestate_id = None
        #     for num_id, nom in state_listing.items():
        #         if nom == identifiant:
        #             gamestate_id = num_id
        #             break
        #     if gamestate_id is None:
        #         assert 0, "state name not found: " + identifiant
        # else:
        #     gamestate_id = identifiant
        gamestate_id = identifiant
        return self.assoc_id_state_obj[gamestate_id]
