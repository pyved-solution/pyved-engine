from ... import dep_linking


pygame = dep_linking.pygame


def clip(surf, x, y, x_size, y_size):
    # WTF bro? Part of original code commented:
    # handle_surf = surf.copy()
    clip_r = pygame.Rect(x, y, x_size, y_size)
    # handle_surf.set_clip(clipR)
    image = surf.subsurface(clip_r)  # handle_surf.get_clip())

    # pr port ca vers Web Ctx
    # ya donc que 2 operations a emuler convenablement: .subsurface & .copy
    return image.copy()


def swap_color(img, old_c, new_c):
    img.set_colorkey(old_c)
    surf = img.copy()
    surf.fill(new_c)
    surf.blit(img, (0, 0))
    return surf


def load_font_img(font_img, font_color, precomp_letter_widths=None, verbose=False):
    fg_color = (255, 0, 0)
    bg_color = (0, 0, 0)
    # font_img = pygame.image.load(path).convert()
    valid_letter_h = font_img.get_height()

    # N.B. theres a BUG when interactin with KataSDK, thats why I have
    # commetend the line below.
    # Hence ktg-webapp does not crash but it cannot swap color.
    # TODO: fix the bug Asap!

    # font_img = swap_color(font_img, fg_color, font_color)
    last_x = 0

    letter_widths = list()
    if precomp_letter_widths:
        letter_widths.extend(precomp_letter_widths)
    else:
        # compute dynamically, by using >>Surface.get_at(xy_coords)<<
        print('*** ------------ Dyn computing letters_widths -------------- ***')
        for x in range(0, font_img.get_width()):
            colorinfos = font_img.get_at((x, 0))
            if colorinfos[0] == 127:
                tmpw = x - last_x
                letter_widths.append(tmpw)
                last_x = x + 1
            x += 1

    # algo (STEP2) use the letter_width to produce letter_rects
    letter_rects = list()
    cumul = 0
    for given_letter_w in letter_widths:
        letter_rects.append([cumul, 0, given_letter_w, valid_letter_h])
        # - deprec
        # letters.append(
        #     clip(font_img, last_x, 0, tmpw, tmph)
        # )
        cumul += given_letter_w + 1

    # - deprec
    # for letter in letters:
    #     letter.set_colorkey(bg_color)

    # - verbose output, useful to DEBUG
    if verbose:
        card_l = len(letter_rects)
        print('*debug ImgBasedText*')
        print(f' ... source={path}')
        print(f' ... num of letters={card_l}')
        print(f' ... rects={letter_rects}')
        print(f' ... letter_spacings {letter_widths}')
    return letter_rects, letter_widths, font_img.get_height()


class ImgBasedFont:
    # use_colorkey_flag = True  # this is a hotfix for the webctx where on needs to not use colorkey val
    precomputed_widths_data = None
    debugmode_flag = False

    def __init__(self, color, img=None, path=None):
        if (path is None) and (img is None):
            raise ValueError('using the ImgBasedFont requires you to pass either a "path" or an "img" named argument!')
        if img is not None:
            if path is not None:
                print('### warning: unused argument "path" passed to ImgBasedFont, as the "img" argument is sufficient')
            if not isinstance(img, pygame.Surface):
                raise ValueError('unexpected data type for parameter img! Expected: pygame.Surface')
            self._spr_sheet_like = tmp = img
        else:
            self._spr_sheet_like = tmp = pygame.image.load(path)

        if self.precomputed_widths_data:
            triplet = load_font_img(tmp, color, precomp_letter_widths=self.precomputed_widths_data,
                                    verbose=self.debugmode_flag)
        else:
            triplet = load_font_img(tmp, color)

        self.letters_rects, self.letter_spacing, self.line_height = triplet
        self.font_order = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
            'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '.', '-',
            ',', ':', '+', '\'', '!', '?', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '(', ')',
            '/', '_', '=', '\\', '[', ']', '*', '"', '<', '>', ';', '#', '$', '%', '@', '{', '}', '`',
            '~'
        ]
        self.letter_to_idx = dict()
        for idx, one_char in enumerate(self.font_order):
            self.letter_to_idx[one_char] = idx

        self.space_width = self.letter_spacing[self.font_order.index('_')]
        self.base_spacing = 1
        self.line_spacing = 2

    def get_linesize(self):  # stick to pygame interface
        return 11  # TODO implement properly plz! 11 is hardset comes from 11px the PNG height gibson0_font

    def size(self, sample_txt):  # stick to pygame interface
        return self.width(sample_txt), self.get_linesize()

    def width(self, text):
        text_width = 0
        for char in text:
            if char == ' ':
                text_width += self.space_width + self.base_spacing
            else:
                try:
                    idx = self.font_order.index(char)
                except ValueError:
                    # generic char
                    print('cannot comp width for: ', char)
                    idx = self.font_order.index('_')
                text_width += self.letter_spacing[idx] + self.base_spacing

        return text_width

    # ---
    # add-on, only to be compatible with the pygame interface
    def render(self, gtext, antialias, color, bgcolor=None):
        rez = pygame.Surface((self.width(gtext), self.get_linesize()), pygame.SRCALPHA)

        # ancien code -

        # if not self.NO_CK_MODE:
        #     upink = (255, 0, 255)  # ugly pink
        #    rez.fill(upink)
        # self._xrender(gtext, rez, (0, 0))
        # if not self.NO_CK_MODE:
        #     rez.set_colorkey(upink)

        # nouveau code -
        # avant, tt ce bout cetait dans
        # def _xrender(self, text, targ_surf, loc, line_width=0)

        text = gtext
        targ_surf = rez
        loc = (0, 0)

        # - deprec for now, DO NOT DELETE, it could be useful someday soon (today is november 1st)
        # if line_width:
        #     spaces = []
        #     x = 0
        #     for i, char in enumerate(text):
        #         if char == ' ':
        #             spaces.append((x, i))
        #             x += self.space_width + self.base_spacing
        #         else:
        #             x += self.letter_spacing[self.font_order.index(char)] + self.base_spacing
        #     line_offset = 0
        #     for i, space in enumerate(spaces):
        #         if (space[0] - line_offset) > line_width:
        #             line_offset += spaces[i - 1][0] - line_offset
        #             if i != 0:
        #                 text = text[:spaces[i - 1][1]] + '\n' + text[spaces[i - 1][1] + 1:]

        # escaped_chars ARE ['\n', ' ', '\r']
        x_offset = y_offset = 0
        for char in text:
            if char == '\n':
                y_offset += self.line_spacing + self.line_height
                x_offset = 0
            elif char == ' ':
                x_offset += self.space_width + self.base_spacing
            elif char == '\r':
                pass
            else:
                # surf.blit(self.letters[self.font_order.index(char)], (loc[0] + x_offset, loc[1] + y_offset))
                tmpr = self.letters_rects[self.letter_to_idx[char]]
                targ_surf.blit(self._spr_sheet_like, (loc[0] + x_offset, loc[1] + y_offset), area=tmpr)
                x_offset += self.letter_spacing[self.font_order.index(char)] + self.base_spacing

        return rez
