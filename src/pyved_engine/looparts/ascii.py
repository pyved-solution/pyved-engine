"""
all shards/looparts elements start the same way
"""

# engine_link = pe_vars = None
from ..concr_engin import pe_vars
from ..concr_engin import core


engine_link = core.ref_engine()


# - constants
# character set that allows to draw a box with single line around it
CODE_LINE_VERT = 16 * 11 + 3
CODE_LINE_NE = 16 * 12 - 1
CODE_LINE_SW = 16 * 12 + 0
CODE_LINE_NW = 16 * 13 + 10
CODE_LINE_HORZ = 16 * 12 + 4
CODE_LINE_SE = 16 * 13 + 9

# the character that allows to fill the space
CODE_FILL = 13 * 16 + 11
# all
KNOWN_CODES = (
    CODE_LINE_VERT, CODE_LINE_HORZ,
    CODE_LINE_NE, CODE_LINE_SW, CODE_LINE_SE, CODE_LINE_NW,
    CODE_FILL
)

# embedded png files white fg, black bg. I used base64.b64encode(fptr)...
# Use base64.b64decode(encoded) to decode!
_EMB_TILEMAPS_PNGF = {
    8: b'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',
    10: b'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',
    12: b'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',
    16: b'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',
    20: b'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'
}

# global vars
_lastcol = _lastrow = None
_sm_ready = False

_char_size = None
_curr_spritesheet = None
_screen = _matrix = None

# variable _alphabet is defined at init
_alphabet = None


# -------------------------------------------------
#  PUBLIC module-level functions
# -------------------------------------------------
def init(chosen_char_size=None):
    global _screen, _matrix, _sm_ready, _lastcol, _lastrow, _char_size, _alphabet
    if chosen_char_size is None:
        _char_size = 12  # default
    else:
        omega_sizes = _EMB_TILEMAPS_PNGF.keys()
        if chosen_char_size not in omega_sizes:
            raise NotImplementedError(
                'The size specified for the .ascii submodule isnt supported, valid values are:', omega_sizes
            )
        _char_size = chosen_char_size

    _sm_ready = True
    _screen = pe_vars.screen
    scrw, scrh = _screen.get_size()
    adhocw = scrw // _char_size
    adhoch = scrh // _char_size
    if adhocw != scrw / _char_size:
        raise ValueError('div tombe pas juste pour calculer w')
    if adhoch != scrh / _char_size:
        raise ValueError('div tombe pas juste pour calculer h')
    _matrix = engine_link.struct.IntegerMatrix((adhocw, adhoch))
    _lastcol = -1 + adhocw
    _lastrow = -1 + adhoch

    _alphabet = _KFont()


def cpos_to_screen(cpos):
    i, j = cpos
    return i * _char_size, j * _char_size


def get_char_size():
    return _char_size


def increm_char_size():
    loop = [8, 10, 12, 16, 20]
    pos = loop.index(_char_size)
    pos = (pos + 1) % len(loop)
    set_char_size(loop[pos])





def is_ready():
    global _sm_ready
    return _sm_ready


def reset():
    global _sm_ready
    _sm_ready = False
    # TODO permettre de remettre a zero le buffer


def flush():
    pass  # TODO use a buffer for put_char, then use flush to draw everything on screen


def get_bounds():
    return _lastcol + 1, _lastrow + 1


def is_inside(ij_coords):
    i, j = ij_coords
    return -1 < i < _lastcol + 1 and -1 < j < _lastrow + 1


def put_char(identifier, arraypos, fgcolor, bgcolor=None, dest_surf=None):
    if bgcolor is None and identifier == ' ':  # skip if nothing to show
        return

    if _screen is None:
        raise Exception('put_char called but the .ascii submodule has not been init!')
    if fgcolor == (255, 255, 255):
        good_s = _alphabet.fetch(identifier)
    else:
        good_s = _alphabet.render([identifier, ], fgcolor, bgcolor)
    if dest_surf:
        target_s = dest_surf
    else:
        target_s = _screen
    target_s.blit(good_s, (_char_size * arraypos[0], _char_size * arraypos[1]))


def get_charsize():  # like a property, but on module => read-only var.
    return _char_size


# def paste(self, src_surf, pos):
#     self.screen.blit(src_surf, (pos[0]*_char_size, pos[1]*_char_size))
_corresp_table = dict()


def mapping_letter_tileset_idx(lettre):
    global _corresp_table
    # corresp caracteres & indice tile
    nbparcol = 16
    if not len(_corresp_table):  # empty dict
        for y in range(32, 32 + nbparcol * 9):
            _corresp_table[chr(y)] = y

    if lettre in KNOWN_CODES:
        return lettre
    if lettre == '/':
        return 3 * nbparcol - 1
    if lettre == '\\':
        return 6 * nbparcol - 4
    if lettre in _corresp_table:
        return _corresp_table[lettre]
    import binascii
    print('*warning:couldnt map letter to tileset idx: {}[{}]'.format(lettre, str(binascii.hexlify(lettre.encode()))))

    return 0


def screen_to_cpos(pos):
    a, b = pos[0] // _char_size, pos[1] // _char_size
    return a, b


def set_char_size(v):
    global _char_size, _curr_spritesheet, _lastcol, _lastrow
    if v not in _EMB_TILEMAPS_PNGF.keys():
        raise ValueError('cannot set size ', v)
    _char_size = v

    import base64  # to decode images
    import io  # to read from binary buffers

    decoded = base64.b64decode(_EMB_TILEMAPS_PNGF[_char_size])
    filelike_bdata = io.BytesIO(decoded)
    _curr_spritesheet = engine_link.image_load(filelike_bdata)
    _curr_spritesheet.set_colorkey('black')

    if _KFont.inst:
        _KFont.inst.surf = _curr_spritesheet
        _KFont.inst.cached_letters.clear()  # reset cache!

    # refresh gl variables
    _last_col = -1 + engine_link.defs.STD_SCR_SIZE[0] // _char_size
    _last_row = -1 + engine_link.defs.STD_SCR_SIZE[1] // _char_size


# -------------------------------------------------
#  hidden module elements
# -------------------------------------------------
class _AsciiArt:
    def __init__(self, w, h, data=None):
        self.size = (w, h)
        self.data = data


class _KFont:
    inst = None

    def __init__(self):
        self.cached_letters = dict()

        self.__class__.inst = self
        if _curr_spritesheet is None:
            set_char_size(_char_size)  # initialize tileset
        self.surf = _curr_spritesheet

    def render(self, karray_or_txt, fg_color, bg_color=None):
        if isinstance(karray_or_txt, str):
            inp = list(karray_or_txt)
        else:
            inp = karray_or_txt
        rez = engine_link.surface_create((_char_size * len(inp), _char_size))
        rez.fill((0, 0, 0))
        char_destpos = [0, 0]
        for elt in inp:
            s = self.fetch(elt)
            rez.blit(s, char_destpos)
            char_destpos[0] += _char_size
        # replace fg color
        fres = engine_link.surface_create((_char_size * len(inp), _char_size))
        if bg_color is None:
            fres.fill((255, 0, 255))
            fres.set_colorkey((255, 0, 255))
        else:
            fres.fill(bg_color)

        engine_link.transform.threshold(
            fres, rez, (255, 255, 255), (0, 0, 0), fg_color, inverse_set=True
        )
        return fres

    def fetch(self, k):
        k = mapping_letter_tileset_idx(k)

        nbparcol = 16

        if not isinstance(k, int):
            raise ValueError('try to fetch by char code but that is not an int')

        if k in self.cached_letters:
            r = self.cached_letters[k]
        else:
            r = engine_link.surface_create((_char_size, _char_size)).convert()
            r.fill((255, 0, 255))
            r.blit(
                self.surf, (0, 0), (_char_size * (k % nbparcol), _char_size * (k // nbparcol), _char_size, _char_size)
            )
            r.set_colorkey((255, 0, 255))
            self.cached_letters[k] = r
        return r
