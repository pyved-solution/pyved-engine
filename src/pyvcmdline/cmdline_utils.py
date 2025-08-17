import json
import os
import re
import shutil
import time

from . import bundle_ops
from . import server_ops as _netw


class MetadatEntries:
    # what you find below should match what is written in the spare_parts/metadat_format.json,
    # and this is useful to avoid harmful typos when implementing various pyv-cli subcommands
    GameTitle = 'title'
    Slug = 'slug'
    Genre = 'game_genre'
    Author = 'author'
    Date = 'build_date'
    Libs = 'dependencies'

    # define our default values...
    DefaultAuthor = 'Unknown'


# private constants
BASIC_LAUNCH_GAME_SCRIPT_LOC = ('spare_parts', 'launch_game0.py')
NETW_LAUNCH_GAME_SCRIPT_LOC = ('spare_parts', 'launch_game1.py')

# private alias
fpath_join = os.path.join


def copy_launcher_script(bundlename, basic_bundle=True):
    """
    sélectionne le bon script & le copie vers le bundle identifié par bundlename
    """
    # prepare the launch_game.py script
    root_pyvcli = os.path.dirname(os.path.abspath(__file__))
    ylist = BASIC_LAUNCH_GAME_SCRIPT_LOC if basic_bundle else NETW_LAUNCH_GAME_SCRIPT_LOC
    src_file = fpath_join(os.path.join(root_pyvcli, *ylist))

    filename = f"{bundle_ops.RUNGAME_SCRIPT_NAME}.py"
    dest_file = fpath_join(os.getcwd(), bundlename, filename)

    # Nota Bene:
    # shutil.copy2 preserves the original metadata, copy doesnt
    # here, i can use copy, as launch_game.py metadata doesnt matter
    shutil.copy(src_file, dest_file)


def create_folder_and_serialize_dict(folder0_name, data_dict):
    # Check if the folder exists, create it if not
    folder1_name = fpath_join(folder0_name, 'cartridge')
    if not os.path.exists(folder1_name):
        os.makedirs(folder1_name)
    # Serialize the dictionary using JSON and create a JSON file
    json_file_path = fpath_join(folder1_name, 'metadat.json')
    with open(json_file_path, 'w') as json_file:
        json.dump(data_dict, json_file, indent=4)


def recursive_copy(source_folder, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    for item in os.listdir(source_folder):
        source_item = fpath_join(source_folder, item)
        destination_item = fpath_join(destination_folder, item)
        if os.path.isdir(source_item):
            recursive_copy(source_item, destination_item)
        else:
            shutil.copy2(source_item, destination_item)


def test_isfile_in_cartridge(filename, bundle_name) -> bool:
    wrapper_folder = fpath_join(os.getcwd(), bundle_name)
    # TODO support for frozen bundles needs to be added here
    # cartridge_folder = fpath_join(wrapper_folder, 'cartridge')
    adhoc_folder = wrapper_folder
    targ = os.path.sep.join((adhoc_folder, filename))
    return os.path.isfile(targ)


# Load the metadata format definition
def load_metadata_format(file_path: str):
    with open(file_path, 'r') as f:
        return json.load(f)


# Function to check if a value matches the expected type
def check_type(value, expected_type):
    if expected_type == "str" and isinstance(value, str):
        return True
    elif expected_type == "bool" and isinstance(value, bool):
        return True
    elif expected_type == "list" and isinstance(value, list):
        return True
    elif expected_type == "dict" and isinstance(value, dict):
        return True
    return False


def verif_mdata_hot_bundle(mdat_obj) -> str:
    script_dir = os.path.dirname(os.path.realpath(__file__))
    mtd_format = load_metadata_format(fpath_join(script_dir, 'spare_parts', 'metadat_format.json'))
    return verify_metadata(mdat_obj, mtd_format)


def verify_metadata(mdat_obj, given_metadata_format) -> str:
    """
    Confirm that the metadata contains all required fields and follows the specified format.
    Returns a string if something is missing or invalid.
    """
    for key, field_info in given_metadata_format.items():
        # Check for the existence of required keys (all keys are required)
        if key not in mdat_obj:
            return f'Missing key: {key}'

        # Check for type correctness
        value = mdat_obj[key]
        expected_type = field_info["type"]
        if not check_type(value, expected_type):
            return f'Invalid type for key: {key}. Expected {expected_type}, got {type(value).__name__}'

        # If it’s a list, check if the items type is correct
        if expected_type == "list" and "items_type" in field_info:
            items_type = field_info["items_type"]
            if not all(check_type(item, items_type) for item in value):
                return f'Invalid list items for key: {key}. Expected {items_type}'

    # Specific checks for some fields
    pyved_found = False
    for elt in mdat_obj['dependencies']:
        if elt[0] == "pyved_engine":
            pyved_found = True
            break
    if not pyved_found:
        return 'Abnormal dependencies list detected: "pyved_engine" isnt listed'

    # We also need to test whether Y or N, categories specified are valid
    # from a cloud storage perspective!
    if (not isinstance(mdat_obj['game_genre'], list)) or (len(mdat_obj['game_genre']) == 0):
        return 'Invalid metadat format: value tied to "game_genre" has to be a list with non-zero length'
    ok_game_genres = _netw.fetch_remote_game_genres()
    for elt in mdat_obj['game_genre']:
        if elt not in ok_game_genres:
            return f'Game genre "{elt}" rejected by the Kata.Games system, please contact an Admin, or replace value'

    print('Metadata looks fine *** OK')


def read_metadata(bundle_name, specific_dir=None):
    # Check if the folder exists, otherwise we'll throw an error
    if specific_dir is None:
        wrapper_bundle = os.path.join(os.getcwd(), bundle_name)
    else:
        wrapper_bundle = os.path.join(specific_dir, bundle_name)
        print('reading metadat...')
        print('looking in:', wrapper_bundle)

    cartridge_folder = os.path.join(wrapper_bundle, 'cartridge')
    if os.path.exists(cartridge_folder):
        adhoc_folder = cartridge_folder
        # raise ValueError('ERR! Bundle format isnt valid, cartridge structure is missing')
    elif os.path.exists(wrapper_bundle):
        adhoc_folder = wrapper_bundle
    else:
        raise FileNotFoundError(f'ERR! Cannot find metadat in the game bundle ({bundle_name})')

    # need to open cartridge, read metadata,
    whats_open = os.path.sep.join((adhoc_folder, 'metadat.json'))
    # print('READING', whats_open, '...')
    f_ptr = open(whats_open, 'r')
    obj = json.load(f_ptr)
    f_ptr.close()
    return obj


def rewrite_metadata(bundle_name, blob_obj, specific_dir=None):
    if specific_dir is None:
        tdir = os.getcwd()
    else:
        tdir = specific_dir
    wrapper_bundle = os.path.join(tdir, bundle_name)
    cartridge_folder = wrapper_bundle  #os.path.join(wrapper_bundle, 'cartridge')
    what_to_open = os.path.sep.join((cartridge_folder, 'metadat.json'))
    print(f'REWRITING file {what_to_open}...')
    with open(what_to_open, 'w') as fptr:
        json.dump(blob_obj, fptr, indent=2)


def do_bundle_renaming(source, dest):
    print('Renaming the game bundle...')
    print(f'{source} --> {dest}')
    if os.path.isdir(dest):
        raise ValueError(f'cannot rename game bundle, because {dest} already exists in the current folder')
    md_obj = read_metadata(source)
    os.rename(source, dest)
    md_obj['slug'] = dest
    rewrite_metadata(dest, md_obj)
    print('OK.')


def has_right_syntax_for_slug(test_identifier):
    ok_pattern = '^[a-zA-Z0-9_]+$'
    return bool(re.match(ok_pattern, test_identifier))


def safe_YN_question(prompt, default_answer):
    full_prompt_msg = f'{prompt} y/n? [Default val={default_answer}]'
    res = input(full_prompt_msg)
    while res not in ('', 'y', 'n', 'Y', 'N'):
        res = input(full_prompt_msg)
    res = res.lower()  # enforce no caps
    if res == '':
        res = default_answer
    return res


def safe_open_question(prompt, default_answer):
    full_prompt_msg = f'{prompt} value? [Default val={default_answer}]'
    res = input(full_prompt_msg)
    if len(res) == 0:
        res = default_answer
    return res


def gen_build_date_now():
    return time.ctime(time.time())


def save_list_of_py_files(directory, metadat_obj):
    """
    Recursively find *.py files récursivement tous les fichiers avec une extension .py dans un dossier donné.
    """
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                # Ajoute le chemin relatif à partir du dossier de base
                python_files.append(
                    os.path.relpath(os.path.join(root, file), directory).replace('\\', '/')
                )

    # Mise à jour de la clé "source_files"
    metadat_obj['source_files'] = python_files

    # Update date de construction
    metadat_obj['build_date'] = gen_build_date_now()


def save_list_of_assets(cartridge_path, metadata):
    # Get the base folder for assets
    asset_base_folder = os.path.join(cartridge_path, metadata.get('asset_base_folder'))

    # Recursive function to find asset files
    def find_asset_files(base_folder, extensions=('.png', '.jpg', '.json')):
        asset_files = []
        for root, _, files in os.walk(base_folder):
            for a_file in files:
                if a_file.lower().endswith(extensions):
                    # Include relative path within asset_base_folder
                    relative_path = os.path.relpath(os.path.join(root, a_file), asset_base_folder)
                    asset_files.append(relative_path)
        return asset_files

    # let's update the asset list now
    metadata['asset_list'] = find_asset_files(asset_base_folder)
