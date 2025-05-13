import importlib
import json
import os


bundle_name, link_to_glvars, pyved_engine_alias = None, None, 'pyved_engine'


# boot_game func relies on that implementation
def prep_libs(cb_func, rel_import_flag, plugins_list):
    global pyved_engine_alias
    for alias, plugin_name in plugins_list:
        if plugin_name == 'pyved_engine':
            import pyved_engine
            plugin_module = pyved_engine.get_engine_router()
            pyved_engine_alias = alias
            getattr(pyved_engine, 'hub').bundle_name = bundle_name
        elif rel_import_flag:
            module_name = f".lib.{plugin_name}"
            plugin_module = importlib.import_module(module_name, __package__)
        else:
            module_name = f"lib.{plugin_name}"
            plugin_module = importlib.import_module(module_name)
        cb_func(alias, plugin_name, plugin_module)


# boot_game func relies on that implementation
def game_execution(metadata, gdef_module, **kwargs):
    global link_to_glvars, pyved_engine_alias

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

    pyv = getattr(link_to_glvars, pyved_engine_alias)

    pyv.bootstrap_e()
    pyv.preload_assets(
        metadata,
        prefix_asset_folder=adhoc_folder + os.sep + metadata['asset_base_folder'] + os.sep,
        prefix_sound_folder=adhoc_folder + os.sep + metadata['sound_base_folder'] + os.sep
    )
    pyv.run_game(
        getattr(gdef_module, 'init'),
        getattr(gdef_module, 'update'),
        getattr(gdef_module, 'close'),
        **kwargs
    )

import sys


def boot_game(mdata_path, **kwargs):
    print('------mdata_path=', mdata_path)

    global bundle_name, link_to_glvars

    cwd = os.getcwd()
    # Ensure that the current working directory is in sys.path
    if cwd not in sys.path:
        sys.path.append(cwd)

    with open(mdata_path, 'r') as fp:
        metadata = json.load(fp)
        #try:
        #    from cartridge import glvars as c_glvars
        rel_imports = False
        #except ModuleNotFoundError:
        #    from .cartridge import glvars as c_glvars
        #    rel_imports = True
        pck_name = os.path.basename(os.path.dirname(mdata_path))
        module_name = f"{pck_name}.glvars"
        c_glvars = importlib.import_module(module_name)

        link_to_glvars = c_glvars  # glvars becomes available elsewhere
        lib_list = list()
        for elt in metadata['dependencies']:
            lib_id = elt[0]
            if len(elt) > 2:
                alias = elt[2]
                lib_list.append((alias, lib_id))
            else:
                lib_list.append((lib_id, lib_id))
        bundle_name = metadata['slug']
        prep_libs(c_glvars.register_lib, rel_imports, lib_list)
        if c_glvars.has_registered('network'):  # manually fix the network lib (retro-compat)
            getattr(c_glvars, c_glvars.get_alias('network')).slugname = metadata['slug']

        # if not rel_imports:
        #     from cartridge import gamedef
        # else:
        #     from .cartridge import gamedef
        module_name = f"{pck_name}.gamedef"
        gamedef = importlib.import_module(module_name)
        # old:
        # gamedef = importlib.import_module('gamedef', pck_name)
        game_execution(metadata, gamedef, **kwargs)
