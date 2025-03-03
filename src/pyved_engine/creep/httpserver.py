import urllib.parse as urlparse
import urllib.request as urll
from urllib.parse import urlencode
from ...engine.foundation import conf_eng as cgmconf
from ...alpha_pyg.Singleton import Singleton
from ...engine import runs_in_web


@Singleton
class HttpServer:
    def __init__(self):
        self._dev_mode = True
        self._host_str = None
    #     self._default_php_script = None
    #
    # def set_default_script(self, url):
    #     self._default_php_script = url

    def get_gtm_app_url(self):
        return 'https://games.gaudia-tech.com/gtm_app/'

    def get_ludo_app_url(self):
        return 'https://games.gaudia-tech.com/ludo_app/'

    def set_debug_info(self, val):
        self._dev_mode = val

    def __send_get_request(self, url):
        if self._dev_mode:
            print()
            print('---DEBUG NETW.---')
            print('send_get_request')
            print('method GET proxied')
            print(str(url))
            print('...')

        if cgmconf.runs_in_web():
            from browser import ajax, window

            temppp = '0x999'
            def ma_fonc(result):
                nonlocal temppp  # access the outer scope
                # window.console.log('kikoooooo on a vrai resulta la' + str(result))
                temppp = result.text

            ajax.get(url, blocking=True, oncomplete=ma_fonc)
            res = temppp  # json
        else:
            req = urll.Request(url)
            response = urll.urlopen(req)
            res = response.read().decode('ascii')

        if self._dev_mode:
            print(res)
            print('-----------------')
        return res

    def proxied_post(self, url_script_php, post_fields: dict):
        if self._dev_mode:
            print()
            print('---DEBUG NETW.---')
            print('method POST proxied yyaaaa')
            print(str(url_script_php))
            print(str(post_fields))
            print('...')

        if runs_in_web():
            from browser import ajax, window

            temppp = '0x999'
            def ma_fonc(result):
                nonlocal temppp  # access the outer scope
                # window.console.log('kikoooooo on a vrai resulta la' + str(result))
                # window.console.log(str(result.status))
                temppp = result.text

            window.console.log(post_fields)
            ajax.post(url_script_php, data=post_fields, blocking=True, oncomplete=ma_fonc)
            res = temppp  # json

        else:
            # params = pp.urlencode(post_data_dict)
            # headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            request = urll.Request(url_script_php, urlencode(post_fields).encode())
            res = urll.urlopen(request).read().decode('ascii')

        if self._dev_mode:
            print(res)
            print('-----------------')

        return res  # -> json format str

    # def remote_func(self, rem_func_name, dico_params, url_script_php=None):
    #     """
    #     fonction générique envoyant une requête HTTP vers le serveur,
    #     indispensable, mais quasi-jamais utilisée ! (usage déconseillé)
    #
    #     :param url_script_php: URL + script PHP à exécuter e.g. http://games.gaudia-tech.com/brutos/legacy/bopvp.php
    #     :param rem_func_name: valeur pr le paramètre spécial "func", détermine le cas à traiter côté serveur
    #     :param dico_params: repr. des associations nom_param_get <> valeur_pour_ce_param
    #     :return: réponse HTTP brute, peut-être None
    #     """
    #
    #     if url_script_php is None:
    #         assert self._default_php_script
    #         url_script_php = self._default_php_script
    #
    #     if dico_params is None:
    #         dico_params = dict()
    #
    #     if rem_func_name is not None:
    #         dico_params['func'] = rem_func_name
    #
    #     if len(dico_params) > 0:
    #         suffix = urlparse.urlencode(dico_params)
    #         a_envoyer = url_script_php + '?' + suffix  # signe de la methode GET
    #     else:
    #         a_envoyer = url_script_php
    #
    #     return self.__send_get_request(a_envoyer)

    def proxied_get(self, url, get_params):
        if len(get_params) > 0:
            suffix = urlparse.urlencode(get_params)
            a_envoyer = url + '?' + suffix  # signe de la methode GET
        else:
            a_envoyer = url
        if self._dev_mode:
            print(a_envoyer)
        return self.__send_get_request(a_envoyer)
