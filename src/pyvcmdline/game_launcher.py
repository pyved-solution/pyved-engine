import importlib
import json
import os
import sys


bundle_name, game_glvars, pyved_engine_alias = None, None, 'pyved_engine'


# boot_game func relies on that implementation
def prep_libs(cb_func, rel_import_flag, plugins_list):
    # deprecated: rel_import_flag always False since May2025

    global pyved_engine_alias
    for mlib_chosen_alias, micro_lib_name in plugins_list:
        if micro_lib_name == 'pyved_engine':
            import pyved_engine
            plugin_module = pyved_engine.get_engine_router()
            pyved_engine_alias = mlib_chosen_alias
            getattr(pyved_engine, 'hub').bundle_name = bundle_name

        # elif rel_import_flag:
        #    module_name = f".lib.{plugin_name}"
        #    plugin_module = importlib.import_module(module_name, __package__)
        else:
            module_name = f"{bundle_name}.micro_libs.{micro_lib_name}"
            print('--->game launcher will import micro lib:', module_name)
            plugin_module = importlib.import_module(module_name)

        print(f" * calling inner_glvars register on:{micro_lib_name}->{mlib_chosen_alias}")
        cb_func(mlib_chosen_alias, micro_lib_name, plugin_module)


# boot_game func relies on that implementation
def game_execution(metadata, gdef_module, **kwargs):
    """
    :param metadata:
    :param gdef_module:
    :param kwargs: will be passed "as is" to the game-specific gamedef.init function
    :return:
    """
    global game_glvars, pyved_engine_alias

    def find_folder(givenfolder, start_path):
        for root, dirs, files in os.walk(start_path):
            if givenfolder in dirs:
                return True

    adhoc_folder = metadata['slug']
    # current_folder = os.getcwd()
    # if find_folder(metadata['slug'], current_folder):
    #     adhoc_folder = os.path.join('.', metadata['slug'], 'cartridge')
    # elif find_folder('cartridge', current_folder):
    #     adhoc_folder = os.path.join('.', 'cartridge')
    # else:
    #     raise FileNotFoundError("ERR: Asset dir for pre-loading assets cannot be found!")

    pyv = getattr(game_glvars, pyved_engine_alias)

    pyv.bootstrap_e()
    pyv.preload_assets(
        metadata,
        prefix_asset_folder=adhoc_folder + os.sep + metadata['asset_base_folder'] + os.sep,
        prefix_sound_folder=adhoc_folder + os.sep + metadata['sound_base_folder'] + os.sep
    )
    # if the game is multiplayer, we need to instantiate a netlayer
    # init network comms, create a model, and force sync it
    if metadata['multiplayer']:
        if 'mode' not in kwargs:
            raise ValueError('for multiplayer game, "mode" HAS TO be either specify in metadat>kwargs or via cmd line')
        pyv.netlayer = pyv.netlayer_factory.build_netlayer(kwargs['mode'], 'client')

    pyv.run_game(
        getattr(gdef_module, 'init'),
        getattr(gdef_module, 'update'),
        getattr(gdef_module, 'close'),
        **kwargs
    )


def boot_game(mdata_path, **cli_kwargs):
    print('------mdata_path=', mdata_path)

    global bundle_name, game_glvars

    cwd = os.getcwd()
    # Ensure that the current working directory is in sys.path
    if cwd not in sys.path:
        sys.path.append(cwd)

    with open(mdata_path, 'r') as fp:
        metadata = json.load(fp)
        pck_name = os.path.basename(os.path.dirname(mdata_path))
        module_name = f"{pck_name}.glvars"
        game_glvars = inner_glvars = importlib.import_module(module_name)

        # TODO nothing to do with the version number??
        lib_list = list()
        for elt in metadata['dependencies']:
            lib_id = elt[0]
            if len(elt) > 2:
                alias = elt[2]
                lib_list.append((alias, lib_id))
            else:
                lib_list.append((lib_id, lib_id))
        bundle_name = metadata['slug']

        # ----
        # prepare libraries
        # ----
        prep_libs(inner_glvars.register_lib, False, lib_list)
        # we HAVE TO manually fix the network microlib (retro-compatibility)
        if inner_glvars.has_registered('network'):
            getattr(inner_glvars, inner_glvars.get_alias('network')).slugname = metadata['slug']

        # if not rel_imports:
        #     from cartridge import gamedef
        # else:
        #     from .cartridge import gamedef
        module_name = f"{pck_name}.gamedef"
        gamedef = importlib.import_module(module_name)
        # old:
        # gamedef = importlib.import_module('gamedef', pck_name)

        synth_kwargs = metadata['kwargs']  # using what is in file, but can be overwritten via line cmd

        for gk, val in cli_kwargs.items():  # print warnings
            if gk in synth_kwargs:
                print(' *warning* ', gk, 'value found in metadat.json gets replaced by the value passed via pyv-cli:',
                      cli_kwargs[gk]
                      )
        synth_kwargs.update(cli_kwargs)
        game_execution(metadata, gamedef, **synth_kwargs)
