import threading

# import urllib.parse as pp
# from http.client import HTTPConnection
from katagames_sdk.capsule.networking.httpserver import HttpServer


class EnvoiAsynchrone2(threading.Thread):
    NB_INST_MAX = 16

    nb_courant_instances = 0

    PORT = None
    HOST_STR = None
    
    def __init__(self, id_req, http_ressource, opt_data, test_timestamp=None):
        cls = self.__class__

        if cls.nb_courant_instances >= cls.NB_INST_MAX:
            raise Exception('Nb. maximum d\' appels asynchrones atteint')

        self.id_req = id_req  # utile pour fournir reponse via CgmEvent !!

        # self.test_timestamp = '1523728737' if (test_timestamp is None) else test_timestamp

        threading.Thread.__init__(self)
        cls.nb_courant_instances += 1

        self.post_data = opt_data  # peut être None si on fait du get, ou set correctement pour du POST

        # - TEMPORAIRE
        # self.server_port = self.__class__.PORT
        # self.host = self.__class__.HOST_STR

        # pr long-polling
        # self.url_pr_server_time = None
        
        self.target_http_ressource = http_ressource
        self.zombie_thread = threading.Event() 
        self.response = None

        # self.cb = None

    # def setup_callback(self, cb):
    #     self.cb = cb

    def __del__(self):
        self.__class__.nb_courant_instances -= 1

    # était utilisé pour le long polling...
    # def stop(self):
    #    pass
        # self.cli_http.close()

    # def f_long_polling_packet(self, ts_arg):
    #     if self.server_port is None:  # si non initialisé
    #         self.server_port = 80
    #         self.host = '192.168.1.99'
    #         self.url_pr_server_time = '/tom/server.php'
    #         self.debug_mode = True
    #
    #         #self.cli_http = HTTPConnection(self.host)
    #         #self.cli_http.connect()
    #
    #     # transmission
    #     msg = self.url_pr_server_time + '?timestamp={}'.format(ts_arg)
    #
    #     res = EnvoiAsynchrone2._commit_to_netw(self.host, msg)
    #     return res

    def run(self):
        url = 'http://{}:{}/{}'.format(EnvoiAsynchrone2.HOST_STR, EnvoiAsynchrone2.PORT, self.target_http_ressource)

        if self.post_data is not None:
            self.response = HttpServer.instance().proxied_post(url, {'data': self.post_data})
        else:
            self.response = HttpServer.instance().proxied_get(url, {})

        self.zombie_thread.set()  # indique que la tâche du thread est terminée
