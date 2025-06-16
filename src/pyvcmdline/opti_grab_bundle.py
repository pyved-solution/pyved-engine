import os
import sys
from concurrent.futures import ThreadPoolExecutor

import requests
from tabulate import tabulate


# Base URL template (with placeholders for REPO_ID, tag, template name)
ROOT_URL_TEMPLATE = "https://raw.githubusercontent.com/pyved-solution/{}/{}/"  # 1st blank->name of the repo
BASE_URL_TEMPLATE = ROOT_URL_TEMPLATE + "{}/"  # blanks 2 and 3-> tag, then template name
REPO_ID = 'game-templates-index'
# -----------------------------------
#  params
# -----------------------------------
localpath_prefix = '.'
specified_tag = "main"  # store the selected tag

# Queue to store download tasks
download_queue = []


# Helper functions
# -----------------------------------
def get_url_to_templ(template_name):
    return BASE_URL_TEMPLATE.format(REPO_ID, specified_tag, template_name)


def get_url_to_root():
    return ROOT_URL_TEMPLATE.format(REPO_ID, specified_tag)


# Function to download files concurrently from the queue
def process_download_queue():
    global download_queue
    with ThreadPoolExecutor(max_workers=5) as executor:
        for url, is_binary, save_path in download_queue:
            executor.submit(download_file, url, save_path, is_binary)


# What-to-download functions
# --------------------------

# Function to fetch and parse the metadata file
def fetch_metadata(template_name):  # TODO right now this only supports NON-FROZEN bundles,
    # need to take into account that a special case exists, right?

    url = get_url_to_templ(template_name) + 'metadat.json'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch metadata for template '{template_name}': {response.status_code}")
    metadata = response.json()  # Parse JSON response

    # Save metadata locally
    localname = metadata['slug']
    base_dir = f"{localpath_prefix}/{localname}/"
    os.makedirs(base_dir, exist_ok=True)
    download_queue.append((url, False, os.path.join(base_dir, 'metadat.json')))
    return metadata


# Function to download a single file
def download_file(url, save_path, binary_data):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Download FAILED! {url} // {response.status_code}")
        return
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if binary_data:
        with open(save_path, "wb") as fptr:
            fptr.write(response.content)
    else:
        with open(save_path, "w", encoding="utf-8") as text_fptr:
            text_fptr.write(response.text)
    print(f"{save_path}")


# Prepare download tasks for launcher and thumbnails
def dl_launcher_n_thumbnails(template_name, metadata):
    localname = metadata['slug']
    base_dir = f"{localpath_prefix}/{localname}/"
    os.makedirs(base_dir, exist_ok=True)

    # Add thumbnails to download queue
    # no need at this point,
    # since as of May25 we support only non-frozen bundles...

    # download_queue.append(
    #    (get_url_to_templ(template_name) + "launch_game.py", False, os.path.join(base_dir, #'launch_game.py')))

    for key in ["thumbnail512x384", "thumbnail512x512"]:
        file_path = metadata[key]
        download_queue.append((get_url_to_templ(template_name) + file_path, True,
                               os.path.join(base_dir, file_path)))


# Prepare download tasks for all files based on metadata
def dl_template_cartridge(template_name, metadata):
    base_url = get_url_to_templ(template_name)
    localname = metadata['slug']
    base_dir = f"{localpath_prefix}/{localname}"
    os.makedirs(base_dir, exist_ok=True)

    # Queue source files
    for file_path in metadata.get("source_files", []):
        download_queue.append(
            (get_url_to_templ(template_name) + file_path, False, os.path.join(base_dir, file_path))
        )

    # Queue assets as binary, including special case for sprite sheets
    asset_base = metadata.get("asset_base_folder", "")
    for asset_file in metadata.get("asset_list", []):
        asset_url = base_url + f"{asset_base}/{asset_file}"
        asset_save_path = os.path.join(base_dir, asset_base, asset_file)

        # If asset is a JSON file, download both the JSON and corresponding PNG sprite sheet
        if asset_file.endswith(".json"):
            download_queue.append((asset_url, True, asset_save_path))  # Add JSON file to download queue

            # Also queue the PNG file with the same base name
            sprite_sheet_png = asset_file.replace(".json", ".png")
            sprite_sheet_url = base_url + f"{asset_base}/{sprite_sheet_png}"
            sprite_sheet_save_path = os.path.join(base_dir, asset_base, sprite_sheet_png)
            download_queue.append((sprite_sheet_url, True, sprite_sheet_save_path))  # Add PNG file to download queue
        else:
            # Normal asset download
            download_queue.append((asset_url, True, asset_save_path))

    # Queue sounds as binary
    sound_base = metadata.get("sound_base_folder", "")
    for sound_file in metadata.get("sound_list", []):
        download_queue.append((get_url_to_templ(template_name) + f"{sound_base}/{sound_file}", True,
                               os.path.join(base_dir, sound_base, sound_file)))

    # Queue data files as binary
    for data_file in metadata.get("data_files", []):
        download_queue.append(
            (get_url_to_templ(template_name) + f"{data_file}", True, os.path.join(base_dir, data_file)))


def game_template_dl(x):
    metadata = fetch_metadata(x)  # Fetch metadata
    dl_launcher_n_thumbnails(x, metadata)
    dl_template_cartridge(x, metadata)  # Queue all downloads
    # Process the download queue concurrently
    process_download_queue()
    print(f"Template '{x}' downloaded successfully.")


def lookup_templ_index():
    # fetch a special file containing a mapping: template_idx<>template_name
    url = get_url_to_root() + 'chosen_templates.csv'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Error when fetching index of templates for Git repo!")

    # Process the CSV content
    mapping_idx_to_name = {}
    csv_content = response.text
    raw_lines = csv_content.strip().splitlines()
    for line in raw_lines[1:]:  # Skip the first line
        rank, name = line.split(",")  # Split each line by comma
        mapping_idx_to_name[int(rank)] = name  # Store in dictionary with rank as int

    table_data = list()
    for rank in range(1, 1 + max(mapping_idx_to_name.keys())):  # IMPORTANT: game template identifiers start at 1 not 0
        name = mapping_idx_to_name[rank]
        table_data.append((rank, name))
    # Print nicely with headers
    print(tabulate(table_data, headers=raw_lines[0].split(','), tablefmt="grid"))
    return mapping_idx_to_name


def select_then_dl():
    flm = lookup_templ_index()
    prompt = 'Select template by specifying its identifier: '
    max_selec = max(flm.keys())
    inp = input(prompt)

    while not inp.isnumeric() or not (0 < int(inp) <= max_selec):
        print(' Invalid answer. Please retry')
        inp = input(prompt)  # prompt user if no argument is provided
    templ_name = flm[int(inp)]
    game_template_dl(templ_name)
    return templ_name


# ----------------------
#  main program, for testing purpose
# ----------------------
if __name__ == '__main__':
    if len(sys.argv) == 1:
        # no extra args
        select_then_dl()
    else:
        my_templ_name = sys.argv[1]  # Use the first argument as the template name
        game_template_dl(my_templ_name)
