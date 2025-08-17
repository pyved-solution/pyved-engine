import json
from typing import List, Dict
from ..concr_engin import core

"""
warning:
the current source-code looks stupid, but it has written that way in order to
avoid several bugs that exist in the pyVM component.
(scaling images, and use .subsurface on these images for cutting sub images)
As long as the pyVM has not bee toroughly debugged and tested,
I recommend not modifying the following code, unless you want to take risks
"""

"""
logic of the current file

1 --Format Detection:
The script checks the type of the frames key in the JSON:
If it's a list → JSON List format.
If it's a dictionary → JSON Hash format.

2 --Parsing Logic:
For the list format, it extracts details from each entry.
For the hash format, it uses the key as the filename and extracts other details from the value.

3 --Class-Based Representation:
Each frame is converted into an instance of the Frame class, which acts as a high-level, unified representation.
Output: The program prints the detected format and the loaded frames.
"""


pyv = core.ref_engine()


class Frame:
    """High-level representation of a frame/sprite read from any spritesheet.json file."""

    def __init__(self, name: str, x: int, y: int, w: int, h: int, rotated: bool, trimmed: bool, source_w: int,
                 source_h: int, duration: int):
        self.filename = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rotated = rotated
        self.trimmed = trimmed
        self.source_w = source_w
        self.source_h = source_h
        self.duration = duration

    def __repr__(self):
        return f"Frame(filename={self.filename}, x={self.x}, y={self.y}, w={self.w}, h={self.h})"


class FrameLoader:
    """Loader to handle JSON list and hash formats."""

    @staticmethod
    def load(json_data: Dict) -> List[Frame]:
        frames = list()

        if "frames" in json_data:
            # using the JSON list format
            if isinstance(json_data["frames"], list):
                imsg = "Detected format: JSON List"
                print(imsg)
                for entry in json_data["frames"]:
                    frames.append(FrameLoader._parse_frame_from_list(entry))
            # using the JSON hash format
            elif isinstance(json_data["frames"], dict):
                imsg = "Detected format: JSON Hash"
                print(imsg)
                for name, entry in json_data["frames"].items():
                    frames.append(FrameLoader._parse_frame_from_hash(name, entry))
            else:
                raise ValueError("Invalid format: 'frames' must be either a list or a dictionary.")
        else:
            raise ValueError("Invalid format: 'frames' key not found in JSON data.")

        return frames

    @staticmethod
    def _parse_frame_from_list(entry: Dict) -> Frame:
        if "sourceSize" not in entry:  # no trimming
            source_size_w, source_size_h = entry["frame"]["w"], entry["frame"]["h"]
        else:
            source_size_w, source_size_h = entry["sourceSize"]["w"], entry["sourceSize"]["h"]
        return Frame(
            name=entry["filename"],
            x=entry["frame"]["x"],
            y=entry["frame"]["y"],
            w=entry["frame"]["w"],
            h=entry["frame"]["h"],
            rotated=False if ("rotated" not in entry) else entry["rotated"],
            trimmed=False if ("trimmed" not in entry) else entry["trimmed"],
            source_w=source_size_w,
            source_h=source_size_h,
            duration=None if ("duration" not in entry) else entry["duration"]
        )

    @staticmethod
    def _parse_frame_from_hash(elt_name: str, entry: Dict) -> Frame:
        if "sourceSize" not in entry:  # no trimming
            source_size_w, source_size_h = entry["frame"]["w"], entry["frame"]["h"]
        else:
            source_size_w, source_size_h = entry["sourceSize"]["w"], entry["sourceSize"]["h"]
        return Frame(
            name=elt_name,
            x=entry["frame"]["x"],
            y=entry["frame"]["y"],
            w=entry["frame"]["w"],
            h=entry["frame"]["h"],
            rotated=False if ("rotated" not in entry) else entry["rotated"],
            trimmed=False if ("trimmed" not in entry) else entry["trimmed"],
            source_w=source_size_w,
            source_h=source_size_h,
            duration=None if ("duration" not in entry) else entry["duration"]
        )


class SpriteSheet:
    def __init__(self, filename_noext_nopath, pathinfo=None, ck=None, is_webhack=None):
        print('Creating the json-based SpriteSheet', filename_noext_nopath)
        if is_webhack is not None:
            p = is_webhack
        elif pathinfo is None:
            p = ''
        else:
            p = pathinfo

        open_img = f'{p}{filename_noext_nopath}.png'
        print('open img->', open_img)
        self.sheet_surf = pyv.image_load(open_img)  # TODO needs to be forbidden -> preload _all philosophy!
        if pathinfo and pathinfo != './':
            p = pathinfo
        json_def_file = open(f'{p}{filename_noext_nopath}.json', 'r')
        jsondata = json.load(json_def_file)

        # -----
        # processing to get info about (a) the meta scale info and (b) the colorkey info
        meta_scale_field = "1"
        meta = jsondata.get("meta", "")
        if meta:
            meta_scale_field = meta.get("scale", meta_scale_field)
            print('[SpriteSheet] image scale after reading meta field:', meta_scale_field)
        else:
            print('[SpriteSheet] no meta field has been found in the json file')
        try:
            chosen_scale_f = float(meta_scale_field)
        except ValueError:
            e_msg = f"[Spritesheet:] WARNING! Cant convert scale '{meta_scale_field}' to float, using default val."
            print(e_msg)
            chosen_scale_f = 1.0
        if ck:
            self.sheet_surf.set_colorkey(ck)

        self.all_names = set()
        # assoc_tmp = dict()
        # y = chosen_scale_f
        # chosen_scale_f = 1.0
        # if isinstance(jsondata['frames'], list):  # we support 2 formats of json desc
        #     for infos in jsondata['frames']:
        #         gname = infos['filename']
        #         self.all_names.add(gname)
        #         args = (infos['frame']['x'] * chosen_scale_f, infos['frame']['y'] * chosen_scale_f,
        #                 infos['frame']['w'] * chosen_scale_f, infos['frame']['h'] * chosen_scale_f)
        #         tempp = self.sheet_surf.subsurface(_hub.pygame.Rect(*args)).copy()
        #         lw, lh = tempp.get_size()
        #         assoc_tmp[gname] = _hub.pygame.transform.scale(
        #             tempp, (y * lw, y * lh)
        #         )
        # else:
        #     for sprname, infos in jsondata['frames'].items():
        #         self.all_names.add(sprname)
        #         args = (infos['frame']['x'] * chosen_scale_f, infos['frame']['y'] * chosen_scale_f,
        #                 infos['frame']['w'] * chosen_scale_f, infos['frame']['h'] * chosen_scale_f)
        #         tempp = self.sheet_surf.subsurface(_hub.pygame.Rect(*args)).copy()
        #         lw, lh = tempp.get_size()
        #         assoc_tmp[sprname] = _hub.pygame.transform.scale(
        #             tempp, (y * lw, y * lh)
        #         )

        # Parse the frames and then build high-level representations
        self.assoc_name_spr = dict()  # next line will populate this
        self._populate_spr_map(
            FrameLoader.load(jsondata),
            chosen_scale_f
        )

    def _populate_spr_map(self, frames_data, mscale):
        """Extract frames from the JSON list format."""
        for single_frame in frames_data:
            self.all_names.add(single_frame.filename)
            _rect_arg = (
                single_frame.x, single_frame.y,
                single_frame.w, single_frame.h
            )
            subsurface = self.sheet_surf.subsurface(pyv.new_rect_obj(*_rect_arg)).copy()
            eff_w, eff_h = subsurface.get_size()
            self.assoc_name_spr[single_frame.filename] = pyv.surface_transform(
                subsurface, (eff_w*mscale, eff_h*mscale)
            )

    def __getitem__(self, item):
        return self.assoc_name_spr[item]
