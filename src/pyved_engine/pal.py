import random as _rand


class _Pal:
    def __init__(self, pal_tuple):
        self.ctable = dict()
        self.listing = list()
        self.names = list()
        for elt in pal_tuple:
            t3 = (elt[1], elt[2], elt[3])
            self.ctable[elt[0]] = t3
            self.listing.append(t3)
            self.names.append(elt[0])

        self._size = len(pal_tuple)

    @property
    def size(self):
        return self._size

    def get_name(self, rgb):
        for nam, desc in self.ctable.items():
            if rgb[0] == desc[0] and rgb[1] == desc[1] and rgb[2] == desc[2]:
                return nam

    def get_rank(self, rgb):
        return self.listing.index(rgb)

    def at_random(self, excl_set=None):
        """
        excl_set can be {0, 3, 8} for example,
        but can also be {'black', 'white', 'orange', 'blue'} for example
        """
        picknumber, exclusion = True, False
        if excl_set:
            if len(excl_set) > self._size:
                raise ValueError('excl_set cannot exclude that many colours!')

            e = None
            for e in excl_set:
                exclusion = True
                break
            if exclusion:
                if not isinstance(e, int):
                    picknumber = False
        else:
            excl_set = set()

        if picknumber:
            omega = list(range(self._size))
            for exck in excl_set:
                omega.remove(exck)
            return self.listing[_rand.choice(omega)]

        omega = list(self.names)
        for exck in excl_set:
            omega.remove(exck)
        return self.ctable[_rand.choice(omega)]

    def next_colorname(self, cname):  # handy for cycling through all the palette
        curr_k = self.names.index(cname)
        k = (curr_k+1) % len(self.names)
        return self.names[k]

    def __getattr__(self, item):
        return self.ctable[item]

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.ctable[item]
        else:
            return self.listing[item]


# ------------------
#  Built-in palettes
# ------------------
_c64pdef = (
    ('black', 0, 0, 0),
    ('white', 255, 255, 255),
    ('red', 138, 20, 22),
    ('cyan', 120, 170, 207),

    ('violet', 204, 68, 204),
    ('green', 100, 184, 70),
    ('blue', 69, 32, 195),
    ('yellow', 207, 207, 101),

    ('orange', 154, 101, 32),
    ('brown', 101, 69, 0),
    ('lightred', 207, 138, 101),
    ('darkgray', 69, 69, 69),

    ('gray', 138, 138, 138),
    ('lightgreen', 170, 239, 138),
    ('lightblue', 160, 162, 255),
    ('lightgray', 170, 170, 170),
)

_cyberpunkdef = (
    ('black', 0, 0, 0),
    ('nightblue', 1, 1, 42),
    ('darkpurple', 50, 20, 80),
    ('darkblue', 40, 40, 68),
    ('gray', 88, 82, 104),
    ('lightblue', 4, 218, 246),  # ('cyan', 115, 255, 254),
    ('cyangreen', 160, 253, 226),
    ('brightgreen', 0, 255, 65),
    ('lightgreen', 100, 221, 153),
    ('green', 106, 126, 105),
    ('brown', 85, 75, 65),
    ('lightbrown', 148, 89, 10),
    ('yellow', 243, 230, 0),
    ('glowinyellow', 222, 254, 71),
    ('paleyellow', 255, 230, 157),
    ('orange', 255, 110, 39),
    ('paleorange', 255, 150, 96),
    ('mud', 53, 21, 9),
    ('bloodstain', 83, 1, 9),
    ('red', 255, 0, 60),
    ('flashypink', 251, 16, 163),
    ('pink', 248, 135, 255),
    ('lightgray', 183, 192, 221),
    ('white', 227, 222, 223)
)

_japan = (
    ('black', 0, 0, 0),
    ('navy', 43, 51, 95),
    ('purple', 126, 32, 114),
    ('green', 25, 149, 156),
    ('brown', 139, 72, 82),
    ('darkblue', 57, 92, 152),
    ('skyblue', 169, 192, 255),
    ('white', 238, 238, 238),
    ('red', 212, 24, 108),
    ('orange', 211, 132, 65),
    ('yellow', 233, 195, 91),
    ('lime', 112, 198, 169),
    ('cyan', 118, 150, 222),
    ('gray', 163, 163, 163),
    ('pink', 255, 151, 152),
    ('peach', 237, 199, 176)
)

_niobe = (
    ('superdarkgreen', 11, 24, 11),
    ('matrixgreen', 0, 143, 17),
    ('peach', 247, 181, 140),
    ('purplegray', 132, 115, 156),
    ('neonpurple', 167, 69, 255),
    ('neongreen', 44, 255, 8)
)

_yudef = (
    ('black', 0, 0, 0),
    ('bright_orange', 254, 112, 0),
    ('brown', 138, 96, 66),
    ('cherry_red', 224, 60, 50),
    ('crimson', 209, 15, 76),
    ('dark_burgundy', 76, 0, 0),
    ('dark_crimson', 153, 21, 21),
    ('dark_green', 0, 61, 16),
    ('dark_sky_blue', 68, 48, 186),
    ('green', 0, 132, 86),
    ('lavender', 204, 104, 228),
    ('leaf_green', 99, 179, 29),
    ('light_gray', 200, 200, 200),
    ('lime_green', 164, 240, 34),
    ('mauve', 120, 52, 80),
    ('medium_gray', 112, 112, 112),
    ('midnight_purple', 52, 0, 88),
    ('mint_green', 88, 245, 177),
    ('navy_blue', 32, 32, 64),
    ('ocean_blue', 0, 106, 180),
    ('olive_yellow', 163, 163, 36),
    ('royal_purple', 150, 0, 220),
    ('rust_orange', 202, 74, 0),
    ('salmon_pink', 254, 98, 110),
    ('sky_blue', 39, 186, 219),
    ('soft_orange', 254, 184, 84),
    ('soil', 164, 128, 128),
    ('sunshine_yellow', 232, 234, 74),
    ('teal_gray', 100, 164, 164),
    ('vibrant_pink', 254, 72, 222),
    ('white', 255, 255, 255),
    ('wine_red', 134, 22, 80)
)


def __getattr__(name):
    return ALL_PALETTES[name]


# ---------------------------@@@-------
#  Palette mapping (the essential part)
# ---------------------------@@@-------
ALL_PALETTES = {
    'c64': _Pal(_c64pdef),  # Commodore 64
    'japan': _Pal(_japan),
    'punk': _Pal(_cyberpunkdef),
    'niobe': _Pal(_niobe),
    'yu': _Pal(_yudef)
}
