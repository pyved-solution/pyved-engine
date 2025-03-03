import csv
import json
import os
from io import StringIO

from .concr_engin import pe_vars


class AssetsStorage:
    def _preload_ncsv_file(self, filename_no_ext, file_prefix, webhack_info=None):
        print('## attempts to load NCSV; args are:', filename_no_ext, file_prefix, webhack_info, '###')

        # filepath = prefix_asset_folder + asset_desc if prefix_asset_folder else asset_desc
        csv_filename = filename_no_ext + '.' + 'ncsv'

        if webhack_info:
            y = webhack_info + csv_filename
        else:
            y = file_prefix + csv_filename
        print('>>>tryin to find data file:', y)
        with open(y, 'r') as file:
            str_csv = file.read()
            f = StringIO(str_csv)
            map_data = list()
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                if len(row) > 0:
                    map_data.append(list(map(int, row)))
            self.csvdata[filename_no_ext] = map_data

    def __init__(self, lowlevel_service, gfx, adhoc_dict: dict, prefix_asset_folder, prefix_sound_folder, debug_mode=False, webhack=None):
        """
        expected to find the (mandatory) key 'images',
        also we may find the (optionnal) key 'sounds'
        """
        self.gfx = gfx

        self.images = dict()
        self.data = dict()
        self.sounds = dict()
        self.fonts = dict()
        self.spritesheets = dict()

        if debug_mode:
            print('*' * 50)
            print(f' CALL to preload assets [webhack value:{webhack}]')
            print('*' * 50)
            print()

        for asset_desc in adhoc_dict['asset_list']:
            if isinstance(asset_desc, str):  # either sprsheet or image
                kk = asset_desc.split('.')
                # print('>>>>>charge file:', kk[0], kk[1])
                # print('prefix_asset_folder?', prefix_asset_folder)

                if kk[1] == 'json':
                    y = prefix_asset_folder
                    if webhack:
                        y = webhack + prefix_asset_folder
                    adhocv = None
                    if webhack:
                        if prefix_asset_folder == './':
                            adhocv = ''
                        else:
                            adhocv = prefix_asset_folder
                    self.spritesheets[kk[0]] = gfx.JsonBasedSprSheet(
                        kk[0], pathinfo=y, is_webhack=adhocv
                    )

                elif kk[1] == 'ttf':  # a >single< TTF font
                    key = "custom_ft"
                    ft_filename = asset_desc

                    if webhack:
                        y = webhack + ft_filename
                    else:
                        y = prefix_asset_folder + ft_filename
                    print('fetching font:', key, ft_filename, f'[{y}]')
                    self.fonts[key] = lowlevel_service.new_font_obj(
                        y,
                        pe_vars.DATA_FT_SIZE
                    )

                else:  # necessarily an image
                    if prefix_asset_folder == './':
                        filepath = asset_desc
                    else:
                        filepath = prefix_asset_folder + asset_desc
                    print('fetching image:', kk[0], filepath)
                    self.images[kk[0]] = lowlevel_service.image_load(filepath)  # TODO most important instr!

        # -------------------------
        # loading sfx files
        # -------------------------
        for snd_elt in adhoc_dict['sound_list']:
            k = snd_elt.split('.')[0]
            filepath = prefix_sound_folder + snd_elt
            if webhack is not None:
                filepath = webhack + filepath
            print('fetching the sound:', k, filepath)
            self.sounds[k] = lowlevel_service.mixer.Sound(filepath)

        # -------------------------
        # loading data files
        # -------------------------
        # For example:
        # - cartridge/conversation.json, or
        # -  my_map.ncsv

        # TODO ! unification/debug.
        #  Right now both assets & data_files can have a .TTF
        prefix = 'cartridge/'

        if webhack:
            for dat_file in adhoc_dict['data_files']:
                fp = os.path.join(webhack, dat_file)
                k, ext = dat_file.split('.')
                if ext == 'json':  # not spritesheets! TODO control "data_hint?"
                    with open(fp, 'r') as fptr:
                        self.data[k] = json.load(fptr)
                elif ext == 'ttf':
                    self.data[k] = lowlevel_service.new_font_obj(fp, pe_vars.DATA_FT_SIZE)

                elif ext == 'ncsv':
                    print('»ncsv webhack:', webhack)
                    self._preload_ncsv_file(k, prefix, webhack_info=webhack)
                else:
                    print(f'*Warning!* Skipping data_files entry "{k}" | For now, only .TTF and .JSON can be preloaded')
            return  # end special case implies we end processing, right there

        for dat_file in adhoc_dict['data_files']:
            k, ext = dat_file.split('.')
            try:
                # fresh filepath
                filepath = prefix + dat_file

                if ext == 'json':
                    with open(filepath, 'r') as fptr:
                        self.data[k] = json.load(fptr)
                elif ext == 'ttf':
                    self.data[k] = lowlevel_service.new_font_obj(filepath, pe_vars.DATA_FT_SIZE)

                elif ext == 'ncsv':
                    self._preload_ncsv_file(k, prefix)

                else:
                    print(f'*Warning!* Skipping data_files entry "{k}" | For now, only .TTF and .JSON can be preloaded')

            except FileNotFoundError:  # TODO refactor to detect case A/B right at the launch script? -->Cleaner code
                new_prefix = os.path.join(pe_vars.bundle_name, prefix)
                print('we modd the prefix -->', new_prefix)

                # try again
                # fresh filepath
                filepath = new_prefix + dat_file
                if webhack is not None:
                    filepath = webhack + filepath
                # ---

                if ext == 'json':
                    with open(filepath, 'r') as fptr:
                        self.data[k] = json.load(fptr)
                elif ext == 'ttf':
                    self.data[k] = lowlevel_service.new_font_obj(filepath, pe_vars.DATA_FT_SIZE)
                elif ext == 'ncsv':
                    self._preload_ncsv_file(k, new_prefix)
