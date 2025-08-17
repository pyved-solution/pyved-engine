import kgame_bundle.defs_mco.glvars as glvars
from coremon_main.events import EventReceiver, EngineEvTypes, EventManager, CgmEvent
from katagames_sdk.capsule.networking.EnvoiAsynchrone2 import EnvoiAsynchrone2
import katagames_sdk.capsule.engine_ground.conf_eng as cgmconf


if cgmconf.runs_in_web():
    from browser import ajax


class AsyncMessagingCtrl(EventReceiver):
    mem_timestamp = None

    def __init__(self):
        super().__init__(True)  # is sticky? YES

        # threads avec envoi / attente en cours
        self.set_of_threads = set()
        self._is_web_mode = cgmconf.runs_in_web()

        if EnvoiAsynchrone2.PORT is None:  # classe non initialisée
            EnvoiAsynchrone2.PORT = glvars.server_port
            EnvoiAsynchrone2.HOST_STR = glvars.server_host
            assert glvars.server_host is not None

    def proc_event(self, ev, source):

        if not self._is_web_mode:
            # - traitement via threading (marche bien en LOCAL)
            if ev.type == EngineEvTypes.ASYNCSEND:
                self.on_async_request(ev)
            elif ev.type == EngineEvTypes.LOGICUPDATE:
                self.on_logic_update(ev)

        else:
            # methode avec cb
            if ev.type == EngineEvTypes.ASYNCSEND:
                backupid = ev.num
                def xoncomplete(req):
                    nonlocal backupid
                    if req.status == 200 or req.status == 0:
                        print((f"%d OK asyncsend gives: " % backupid) + req.text)
                        EventManager.instance().post(CgmEvent(EngineEvTypes.ASYNCRECV, num=backupid, msg=req.text))
                    else:
                        print("error ASYNCSEND" + req.text)

                #req = ajax.Ajax()
                #req.bind('complete', on_complete)

                # send a POST request to the url
                print('+AJAX sending+')
                print('http://{}/{}'.format(glvars.server_host, ev.msg))
                print('post method')
                print('num={}'.format(ev.num))
                print('data={}'.format(ev.data))

                if ev.data is not None:
                    ajax.post('http://{}:{}/{}'.format(glvars.server_host, glvars.server_port, ev.msg), data={'data':ev.data}, oncomplete=xoncomplete)
                else:
                    print('[nodata fiels sent]')
                    ajax.post('http://{}:{}/{}'.format(glvars.server_host, glvars.server_port, ev.msg), oncomplete=xoncomplete)

                #req.open('GET', , ev.msg), True)
                #req.set_header('content-type', 'application/x-www-form-urlencoded')
                # send data as a dictionary
                #req.send({'x': 0, 'y': 1}
                #ev.num, ev.msg, ev.data

    def on_async_request(self, ev):
        print('ds on_async_request')


        print('[AsyncMessagingCtrl] processing async request {}'.format(ev))
        id_req = ev.num
        msg_reseau = ev.msg

        thread = EnvoiAsynchrone2(id_req, msg_reseau, ev.data)  # self.__class__.mem_timestamp)

        # fonctionnement à éviter !
        # if ev.cb is not None:
        #    thread.setup_callback(ev.cb)

        self.set_of_threads.add(thread)
        thread.start()

    def on_logic_update(self, event):
        # aucun thread enregistré
        if len(self.set_of_threads) == 0:
            return

        # si tous les threads continuent leur exécution
        signes_activite = [not t.zombie_thread.isSet() for t in self.set_of_threads]
        if all(signes_activite):
            return

        # on sait que l'exécution d'au moins un thread s'est terminée
        new_set = set()
        for t in self.set_of_threads:
            if not t.zombie_thread.isSet():
                new_set.add(t)
                continue
            new_ev = CgmEvent(EngineEvTypes.ASYNCRECV, num=t.id_req, msg=t.response)
            EventManager.instance().post(new_ev)

        self.set_of_threads = new_set  # on "oublie" ainsi les threads zombie

    def __proc_async_command(self, ev):
        raise NotImplementedError  # TODO utilité ?
        # app_const = AppConstants.instance()
        # # if app_const.get_val('DEV_MODE'):  # désactivé sur serv de prod a cause dun gros bug comm réseau!!
        #     #t = EnvoiAsynchrone(ev.hote, ev.ressource_http)
        #     # print('creation & lancement async worker avec msg: {}'.format(ev.ressource_http))
        # t = AsyncWorker(ev.id_commande, ev.ressource_http)
        # self.set_of_threads.add(t)
        # t.start()  # execute .run() sur le Thread en question, dans un fil d'exécution à part
