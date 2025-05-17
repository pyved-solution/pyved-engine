"""
Contains the implementation of each and every sub_command that should be called from the command-line.
(pyv-cli interface)
private function start with the character '_'
"""
import importlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pprint import pprint as _pprint

import requests

from . import bundle_ops, cmdline_utils
from . import cmdline_utils as _utils
from . import opti_grab_bundle
from . import server_ops as _netw, pyvcli_defs
from . import tileset_creator as _ts_creator
from .cmdline_utils import read_metadata, rewrite_metadata, MetadatEntries, test_isfile_in_cartridge


MODULE_WITH_SERV_CODE = 'netcode'  # module you should put inside the game bundle
SCRIPT_WITH_SERV_CODE = 'run_server.py'
SERV_CODE_START_FUNC = 'exec'


# -------------------------
#  private func
# -------------------------
def pack_game_cartridge(bundl_name, using_temp_dir=True) -> str:
    """
    @param bundl_name:
    @param using_temp_dir:
    @return: a path to the produced ZIP archive
    """
    wrapper_bundle = os.path.join(os.getcwd(), bundl_name)
    zip_precise_target = os.path.join(wrapper_bundle, 'cartridge')

    def _inner_func(source_folder, wanted_zip_filename='output.zip'):
        systmp_directory = tempfile.gettempdir()
        output_zip_path = os.path.join(systmp_directory, wanted_zip_filename)
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_folder)
                    zipf.write(file_path, arcname)
        return output_zip_path

    return _inner_func(zip_precise_target)


def procedure_select_game_genre(mutable_obj):
    """
    @param mutable_obj: metadata to be changed, or no
    """
    prompt0 = 'do yo want to select other genres? Y/[N]'
    prompt1 = 'please select the ones that suit you game,separate by commas:'

    print('it is important to give hints about your game genre. The default genre is')
    if len(mutable_obj['game_genre']) > 1:
        print(','.join(mutable_obj['game_genre']))
    else:
        print(mutable_obj['game_genre'][0])
    inp = input(prompt0)
    while inp not in ('y', 'Y', 'n', 'N', ''):
        print('invalid answer! Re-trying')
        inp = input(prompt0)
    if inp in ('n', 'N', ''):
        return
    # select different genres +failsafe input
    omega = _netw.fetch_remote_game_genres()
    print('server currently accepts these values:', omega)
    print(prompt1)

    is_valid_input = False
    new_genres_list = list()
    while not is_valid_input:
        is_valid_input = True
        inp_g = input()
        all_values = inp_g.split(',')
        for k in range(len(all_values)):
            all_values[k] = all_values[k].lstrip()  # remove spaces char. after the comma, if any
        for elt in all_values:
            if elt not in omega:
                is_valid_input = False
                print('error detected in your input, try again. Example of valid input-> "Experimental,Cards"')
                break
        if is_valid_input:
            new_genres_list.extend(all_values)
    mutable_obj['game_genre'] = new_genres_list


def _query_slug_availability(x):
    # ---------------------------------------
    #  test for slug availability!
    # ---------------------------------------
    CAN_UPLOAD_SCRIPT = 'can_upload.php'
    good_url = _netw.VMSTORAGE_URL + '/' + CAN_UPLOAD_SCRIPT
    slug_avail_serv_truth = requests.get(
        good_url,
        {'slug': x}
    )
    try:
        # error handling after ping the VMstorage remote service
        if slug_avail_serv_truth.status_code != 200:
            raise Exception('[netw error] cant reach the VMstorage service! Contact devs to report the bug, please')
        obj_serv_truth = slug_avail_serv_truth.json()
        if ('success' not in obj_serv_truth) or not obj_serv_truth['success']:
            raise Exception('[protocol error] unexpected result after comms with VMstorage service. Contact devs')
    except json.decoder.JSONDecodeError:
        print('Error! Cant decode reply from server...')
        print('url=', good_url)
        print(slug_avail_serv_truth.text)
    return obj_serv_truth


def ensure_correct_slug(givenslug):
    """
    goal=
    renaming bundle if and only if it is required
    """
    server_truth = _query_slug_availability(givenslug)
    assert (server_truth['success'])
    print('That slug is available' if server_truth['available'] else 'Slug already taken!')
    bval = server_truth['available']

    if not bval:
        print('SUGGESTIONS:')
        for k, elt in enumerate(server_truth['suggestions']):
            print(f'{k}/  {elt}')
        return False, server_truth['suggestions']
    return True, None


# -------------------------
#  public
# -------------------------
def bump(bundle_name):
    """
    Nota Bene: operations bump, share automatically update the list of source files
    """
    active_engine_ver_wdots = pyvcli_defs.read_ver()
    print('trying to bump to current version, that is', active_engine_ver_wdots)

    my_metadat = _utils.read_metadata(bundle_name)
    if my_metadat['frozen']:
        print('cannot bump a frozen game bundle, you will need to upgrade manually and with caution')
    else:
        good_idx = None
        for k, elt in enumerate(my_metadat['dependencies']):
            if elt[0] == 'pyved_engine':
                good_idx = k
                break
        new_str = active_engine_ver_wdots.replace('.', '_')
        my_metadat['dependencies'][good_idx][1] = new_str
        my_metadat['build_date'] = cmdline_utils.gen_build_date_now()
        # the alias that is the element of rank #2 probably stays the same, that is "pyv"
        _utils.rewrite_metadata(bundle_name, my_metadat)


def init(chosen_slug: str) -> None:
    """
    this is the pyv-cli INIT command.
    It creates a new game bundle that is fully operational and based off an existing template.

    :param chosen_slug: a str identifier for your new game
    """
    print(f"Calling sub-command INIT with the game identifier {chosen_slug}")
    print()
    # -------------------------------first ensure we have a valid identifier
    while not _utils.has_right_syntax_for_slug(chosen_slug):
        print('*** WARNING: the selected game identifier is rejected. Expected format:')
        print('Alphanumeric chars: A-Z and a-z, also 0-9 numbers. The underscore _ special character is also allowed')
        chosen_slug = input('try another game identifier(slug): ')

    # TODO: shall we use HERE
    #  the network to test if the name is remotely available?
    #  that feature is already implemented by the 'test' subcommand

    # ------------------------------ perform the template selection > DL > renaming step
    # - deprecated!
    # template_id = ... ce que le mec a choisi
    # adhoc_json_prec = TEMPL_ID_TO_JSON_STR[template_id]
    # metadata = json.loads(adhoc_json_prec)

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # D/L files to the temporary directory
        opti_grab_bundle.localpath_prefix = temp_dir
        old_name = opti_grab_bundle.select_then_dl()

        # read metadata, and update it
        metadata = read_metadata(old_name, temp_dir)

        # set slug
        metadata['slug'] = chosen_slug
        # set title
        tmp = input('whats the name of the game? [Default: Equal to the bundle name]')
        metadata[MetadatEntries.GameTitle] = tmp if len(tmp) > 0 else chosen_slug

        tmp = input('whos the author? [Default: Unknown]')
        metadata[MetadatEntries.Author] = tmp if len(tmp) > 0 else MetadatEntries.DefaultAuthor
        vx_with_dots = pyvcli_defs.read_ver()
        metadata['vmlib_ver'] = vx_with_dots.replace('.', '_')
        metadata[MetadatEntries.Date] = _utils.gen_build_date_now()

        # here, we modify the metadata based on what game genres the user wish to set
        procedure_select_game_genre(metadata)

        # ensure to have registered the latest pyved_engine version +use the default alias:
        metadata[MetadatEntries.Libs]['pyved_engine'] = [
            vx_with_dots.replace('.', '_'), 'pyv'
        ]  # defaut alias for the engine is "pyv"
        rewrite_metadata(old_name, metadata, temp_dir)

        # Create the new dir, then move modified temp. files to the final destination
        final_dest = os.path.join(os.getcwd(), chosen_slug)
        # os.makedirs(final_dest, exist_ok=True)
        shutil.move(os.path.join(temp_dir, old_name), final_dest)

    print(f"temp dir has been destroyed")
    print('subcommand init exits properly.', end='\n\n')
    print('Important remark: do not rename the name of the folder')
    print(f'-->Game bundle {chosen_slug} succesfully created! Now you can type `pyv-cli play {chosen_slug}`')
    print('Go ahead and have fun ;)')


def play(bundle_name, **kwargs):
    devflag_on = kwargs['dev']
    print('dans la cmd', kwargs)
    if '.' != bundle_name and os.path.isdir('cartridge'):
        raise ValueError('launching with a "cartridge" in the current folder, but no parameter "." is forbidden')

    # ------------------------
    #  just checking for errors, on metadat.json
    # ------------------------
    mdata_path = os.path.join(bundle_name, 'metadat.json')
    try:
        with open(mdata_path, 'r') as fptr:
            print(f"game bundle {bundle_name} found. Reading metadata...")
            metadata = json.load(fptr)
        # - debug
        # print('Metadata:\n', metadata)

        # when ktg_services are enabled, we probably wish to set a user session (=login)
        # this will help:
        if metadata['ktg_services']:
            _netw.do_login_via_terminal(metadata, not devflag_on)
        sys.path.append(os.getcwd())
        #if x == '.':
        #    vmsl = importlib.import_module(bundle_ops.RUNGAME_SCRIPT_NAME, None)
        #else:
        from . import game_launcher as vmsl
        # vmsl = importlib.import_module('.' + bundle_ops.RUNGAME_SCRIPT_NAME, x)

        # At this point:
        # assuming that metadata is available, and error-free... We can run boot_game
        vmsl.boot_game(mdata_path, **kwargs)

    except FileNotFoundError:
        print(f'Error: cannot find the game bundle you specified: {bundle_name}')
        print('  Are you sure it exists in the current folder? Alternatively you can try to')
        print('  change directory (cd) and simply type `pyv-cli play`')
        print('  once you are inside the bundle')


def refresh(bundle_name):
    """
    corresponds to the "refresh" operation

    :param bundle_name:
    :return:
    """
    print('list of source files has been updated')
    my_metadat = _utils.read_metadata(bundle_name)
    _utils.save_list_of_py_files(os.path.join(bundle_name, 'cartridge'), my_metadat)
    _utils.save_list_of_assets(os.path.join(bundle_name, 'cartridge'), my_metadat)
    _utils.rewrite_metadata(bundle_name, my_metadat)


def serve(bundle_name, **kwargs) -> None:
    # Print the bundle name for debugging purposes.
    print('>in serve sub-command...')
    print('arg0:', bundle_name)
    print('kwargs:', kwargs)
    # Build the expected directory and file path for the server script.
    server_dir = os.path.join(bundle_name, MODULE_WITH_SERV_CODE)
    server_script_path = os.path.join(server_dir, SCRIPT_WITH_SERV_CODE)

    print('pyved is looking for:', server_script_path)
    if os.path.isfile(server_script_path):
        if kwargs['dev']:
            print("The developer flag is ON... Need to run server in development mode.")
            print('For now, this does NOTHING-- but may be useful later on')
        # Add the bundle directory to sys.path to allow package-relative imports.
        bundle_abs_path = os.path.abspath(bundle_name)
        if bundle_abs_path not in sys.path:
            sys.path.insert(0, bundle_abs_path)

        # TODO achiev this in web context aint that easy. How to overcome the challenge?
        # ---start

        # we 'll need to bind pyv to the 'wrapped' shared vars file
        serv_glvars_module_desc = '.'.join((MODULE_WITH_SERV_CODE, 'shared_code', 'glvars'))
        mvars = importlib.import_module(serv_glvars_module_desc)
        from pyved_engine.EngineRouter import EngineRouter
        from pyved_engine.abstraction.PygameWrapper import PygameWrapper
        mvars.pyv = EngineRouter(PygameWrapper())  # dependency injection
        mvars.pyv.bootstrap_e()
        module_basename, ext = os.path.splitext(SCRIPT_WITH_SERV_CODE)
        file_to_start_server = '.'.join((MODULE_WITH_SERV_CODE, module_basename))

        print(f"using the server launcher {file_to_start_server}")
        launcher_module = importlib.import_module(file_to_start_server)
        if hasattr(launcher_module, SERV_CODE_START_FUNC):
            if 'host' in kwargs and 'port' in kwargs:
                getattr(launcher_module, SERV_CODE_START_FUNC)(**kwargs)  # forwardin kwargs to the server starter func
            else:
                raise ValueError('Error: you need to specify at least "host" and "port" to run a game server!')
        else:
            # error handling at level 2
            print(f"Error: it appears the game doesn't support multiplayer properly \
             (no {SERV_CODE_START_FUNC} function to be found in {SCRIPT_WITH_SERV_CODE}).")
        # ---end

    else:
        # error handling at level 1
        print(f"Error: no {SCRIPT_WITH_SERV_CODE} to be found in the bundle. Are you sure it's a multiplayer game?")


def share(bundle_name, dev_flag_on):
    # TODO in the future,
    #  we may want to create a 'pack' subcommand that would only produce the .zip, not send it elsewhere
    # that pack subcommand would pack and send it to the cwd, whereas the classic pack uses the tempfile/tempdir logic

    # - refresh list of files
    metadat = _utils.read_metadata(bundle_name)
    _utils.save_list_of_py_files(os.path.join(bundle_name, 'cartridge'), metadat)
    rewrite_metadata(bundle_name, metadat)

    slug = metadat['slug']
    if dev_flag_on:  # in devmode, all tests on metadata are skipped
        zipfile_path = pack_game_cartridge(slug)
        print(f'file:{zipfile_path} packed, uploading it now...')
        _netw.upload_my_zip_file(zipfile_path, slug, True)
        return

    err_msg_lines = [
        'ERROR: the "share" is impossible yet, invalid metadat.json detected.',
        'Please use "pyv-cli test BundleName"',
        'in order to get more information and fix the problem'
    ]
    # if we're in prod mode, we HAVE TO pass all tests (slug is valid & available, etc.)
    # before uploading
    if _utils.verify_metadata(metadat) is None:
        slug_correctness = ensure_correct_slug(slug)
        while not slug_correctness[0]:
            tmp = input('what alternative do you choose (please select a number: 0 to 3)? ')
            if not (tmp.isnumeric() and (-1 < int(tmp) < 4)):
                print('invalid input, please retry.')
            else:
                choice = int(tmp)
                slug = slug_correctness[1][choice]
                slug_correctness = ensure_correct_slug(slug)
                # when renaming, both the metadata and the folder name need to be changed
                _utils.do_bundle_renaming(bundle_name, slug)
                bundle_name = slug
        zipfile_path = pack_game_cartridge(bundle_name)
        _netw.upload_my_zip_file(zipfile_path, slug, False)
    else:
        for msg_line in err_msg_lines:  # printing a multi-line error message
            print(msg_line)


def test(bundle_name):
    print(f"Folder targetted to inspect game bundle: {bundle_name}")
    metadat = _utils.read_metadata(bundle_name)

    print('hot bundle') if not metadat['frozen'] else print('bundle:frozen<<<')

    err_message = _utils.verif_mdata_hot_bundle(metadat)
    if err_message is not None:
        raise ValueError(f'The metadata file has an invalid format! ({err_message})')

    # ensure that thumbnails & all assets listed in metadat.json
    # actually exist!
    print('___Testing___ asset existence...')
    files_exp_li = [
        metadat['thumbnail512x384'],
        metadat['thumbnail512x512']
    ]
    for asset_name in metadat['asset_list']:
        files_exp_li.append(metadat['asset_base_folder']+'/'+asset_name)
    for elt in files_exp_li:
        if not test_isfile_in_cartridge(elt, bundle_name):
            raise FileNotFoundError('Thumbnail/Asset not found:', elt)
    print('-->Test Passed', end='\n\n')

    # ensure folder name is ok
    print('___Testing___ folder naming cohesion test...')
    if bundle_name != metadat['slug']:
        y = metadat['slug']
        raise ValueError(f'Either the folder should be named: {y} or the chosen slug is invalid')
    else:
        print('-->Test Passed', end='\n\n')

    # ensure source files listed actually exist
    print('___Testing___ source files existence...')
    to_test = metadat['source_files']
    for elt in to_test:
        if not test_isfile_in_cartridge(elt, bundle_name):
            raise FileNotFoundError('Source file not found:', elt)
    print('-->Test Passed', end='\n\n')

    print('~ Serv-side Slug Availability? ~')
    obj = _query_slug_availability(metadat['slug'])
    if not obj['success']:
        raise ValueError('cannot read info from server!')
    print(' ->', 'yes' if obj['available'] else 'no')
    if not obj['available']:
        print('suggestions:')
        _pprint(obj['suggestions'])


def ts_creation(image_path):
    minsize_given = int(input("Enter the minimal value (in pixels) you believe a tile can have: "))
    spacing = int(input("Enter spacing value please (in pixels): "))

    img_size, tsize_candidates = _ts_creator.suggest_tile_sizes(minsize_given, image_path, spacing)
    print()
    print('-' * 32)
    print('Possible values for tile sizes are:')
    for k, val in enumerate(tsize_candidates):
        print(f'{k} --> {val}')
    chosen_k = int(input('Look at the image, then select the right tile_size candidate.Index? '))
    tsize = tsize_candidates[chosen_k]
    _ts_creator.json_for_tileset(image_path.split('.')[0], img_size, tsize)
    print('JSON file created successfully!')


def upgrade(bundlename):
    """
    ordre dans lequel l'algo procèdera, idéalement:
    [1] rebuild le py_connecteur L (local ctx) à la volée, à partir du fichier de SPEC trouvé
    [2] update des metadata
    [3] constitution d'un module network avec ledit connecteur renommé en __init__.py,
    [4] insertion code network vers le chemin bundle/network
    [5] écrasement launch_game.py par la version moddée
    """

    # TODO:
    # faut fix ce souci
    #
    # a l'heure actuelle, le fichier de API spec n'est PAS utilisé pour générer dynamiquement le pyconnector Local
    # on utilise ce qu'il y a dans pyvcmdline/spare_parts

    # étape 1 préparatifs
    obj = read_metadata(bundlename)
    bundle_location = os.path.join(os.getcwd(), bundlename)
    netw_dir = os.path.join(bundle_location, 'network')
    if obj['ktg_services']:
        print('***WARNING*** ktg_services is already set to true!')
        rez = _utils.safe_YN_question('Do you wish to keep existing files, not rewriting the pyConnector config?', 'y')
        if rez == 'y':
            print('Upgrade operation aborted!')
            return
        else:
            if os.path.isdir(netw_dir):
                shutil.rmtree(netw_dir)

    # ÉTAPE 2: Génération pyConnector, ou prise en compte "spare_parts/network.py"
    # pour le déplacer dans bundle_folder/network
    using_autogen = _utils.safe_YN_question('Do you prefer to use the static pyConnector (no autogen)?', 'y')
    if using_autogen == 'y':
        root_pyvcli = os.path.dirname(os.path.abspath(__file__))
        read_from_netw = os.path.join(root_pyvcli, 'spare_parts', 'network.py')
        target_file = os.path.join(bundle_location, 'network', '__init__.py')
    else:
        print('cant use the autogen, its not implemented just yet')
        raise NotImplementedError

    # TODO améliorations, avec autogen
    # etape 3, création du dossier network dans le bundle folder
    # Pas implem comme il faudrait (là on récupère un network.py statique)
    bundle_location = os.path.join(os.getcwd(), bundlename)
    new_dir = os.path.join(bundle_location, 'network')
    if os.path.isdir(new_dir):
        raise Exception('folder "network" exists in bundle, but non-consistent metadata found')
    os.makedirs(new_dir)

    # étape 4 stricto sensu
    shutil.copy(read_from_netw, target_file)
    obj['ktg_services'] = True
    rewrite_metadata(bundlename, obj)

    # etape 5:
    pyconnector_config_obj = json.loads(
        _netw.template_pyconnector_config_file
    )
    new_url = _utils.safe_open_question('whats the URL for api services?', pyconnector_config_obj['api_url'])
    new_jwt = _utils.safe_open_question('jwt value?', None)
    new_user_id = _utils.safe_open_question('user_id?', None)
    new_username = _utils.safe_open_question('username?', None)

    pyconnector_config_obj['api_url'] = new_url
    pyconnector_config_obj['jwt'] = new_jwt
    pyconnector_config_obj['user_id'] = new_user_id
    pyconnector_config_obj['username'] = new_username
    path_written_config = os.path.join(bundle_location, 'pyconnector_config.json')
    with open(path_written_config, 'w') as fptr:
        fptr.write(json.dumps(pyconnector_config_obj))
        print('file:', path_written_config, 'has been written')

    # etape 6: impacter launch_game.py
    _utils.copy_launcher_script(bundlename, False)
