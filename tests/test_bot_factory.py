# import sys
# sys.path.insert(0, '../src/relevance')

import unittest
from bots.BotFactory import BotFactory, VARIANT_DELIM


# --- Dummies pour les tests ----------------------------------------------- #
class Buylo:
    def __init__(self, name, cfg, w, m, params):
        self.w = w
        self.m = m
        self.params = params


class NoBrainer:
    def __init__(self, name, cfg, w, m):
        self.w = w
        self.m = m


# --- Test cases ------------------------------------------------------------ #
class TestBotFactoryVariants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # On récupère le singleton et on sauvegarde l'état pour restauration
        cls.factory = BotFactory.instance()

        cls.saved = {
            "io_done": cls.factory.io_done,
            "_cls_cache": dict(cls.factory._cls_cache),
            "_params_cache": dict(cls.factory._params_cache),
            "_valid_names_cache": cls.factory._valid_names_cache,
            "_aliases": dict(cls.factory._aliases),
        }

        # On prépare un cache "in-mémoire" minimal pour nos 4 scénarios
        cls.factory._aliases.clear()
        cls.factory._cls_cache.clear()
        cls.factory._params_cache.clear()
        cls.factory._valid_names_cache = None

        # Base 'buylo' → a des paramètres; base 'samuel_brain' → sans paramètres
        cls.factory._cls_cache.update({
            "buylo": Buylo,
            "no_brainer": NoBrainer,
        })
        cls.factory._params_cache.update({
            "buylo": {"neo": (1, 2, 3)},  # une clé de variant valide
            "no_brainer": None,         # pas de module de params
        })

        # On indique à la factory que la découverte I/O est déjà faite
        cls.factory.io_done = True

    @classmethod
    def tearDownClass(cls):
        # Restaure l'état initial du singleton
        cls.factory.io_done = cls.saved["io_done"]
        cls.factory._cls_cache.clear()
        cls.factory._cls_cache.update(cls.saved["_cls_cache"])
        cls.factory._params_cache.clear()
        cls.factory._params_cache.update(cls.saved["_params_cache"])
        cls.factory._valid_names_cache = cls.saved["_valid_names_cache"]
        cls.factory._aliases.clear()
        cls.factory._aliases.update(cls.saved["_aliases"])

    # 1) ✅ buylo_variant_neo -> OK (params requis + fournis)
    def test_build_with_variant_params_ok(self):
        name = "buylo" + VARIANT_DELIM + "neo"
        bot = self.factory.build(name, wallet_model=object(), market_model=object())
        self.assertIsInstance(bot, Buylo)
        self.assertEqual(bot.params, (1, 2, 3))

    # 2) ✅ samuel_brain -> OK (pas de params attendus)
    def test_build_without_params_ok(self):
        bot = self.factory.build("no_brainer", wallet_model=object(), market_model=object())
        self.assertIsInstance(bot, NoBrainer)

    # 3) ❌ buylo -> doit lever une ValueError car variant manquant
    def test_build_missing_variant_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.factory.build("buylo", wallet_model=object(), market_model=object())
        self.assertIn("nécessite un variant", str(ctx.exception))

    # 4) ❌ samuel_brain_variant_zero -> doit lever une ValueError (variant alors qu'aucun params_*)
    def test_build_variant_but_no_params_raises(self):
        name = "no_brainer" + VARIANT_DELIM + "zero"
        with self.assertRaises(ValueError) as ctx:
            self.factory.build(name, wallet_model=object(), market_model=object())
        self.assertIn("indique un variant mais ce bot est pas paramétrable", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
