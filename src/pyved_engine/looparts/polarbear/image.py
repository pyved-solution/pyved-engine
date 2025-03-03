import weakref
from itertools import chain
from ...concr_engin import core


pyv = core.ref_engine()

DEFAULT_COLOR_KEY = (255, 0, 255)
TEXT_COLOR = (240, 240, 50)
# Keep a list of already-loaded images, to save memory when multiple objects
# need to use the same image file.
pre_loaded_images = weakref.WeakValueDictionary()


def truncline(text, font, max_width):
    """
    Truncates a line of text to fit within a specified width without breaking words.

    Parameters:
    text (str): The original text to be truncated.
    font (object): A font object that provides a size method to measure text width.
    max_width (int): The maximum allowable width for the text.

    Returns:
    tuple: (real, done, truncated_text)
        - real (int): The length of the truncated text.
        - done (bool): A flag indicating if the entire text fits (True) or was truncated (False).
        - truncated_text (str): The resulting truncated text that fits within max_width.
    """
    if font.size(text)[0] <= max_width:
        return len(text), True, text
    words = text.split()
    truncated_text = ""
    for word in words:
        if font.size(truncated_text + word)[0] <= max_width:
            truncated_text += word + " "
        else:
            break

    truncated_text = truncated_text.rstrip()  # Remove trailing space
    return len(truncated_text), False, truncated_text


def wrap_line(text, font, max_width):
    """
    Wraps a line of text so that it fits within the specified width.

    Parameters:
    text (str): The original text to be wrapped.
    font (object): A font object that provides a size method to measure text width.
    max_width (int): The maximum allowable width for the text.

    Returns:
    list: A list of wrapped lines.
    """
    wrapped_lines = []
    while text:
        length, done, truncated_text = truncline(text, font, max_width)
        wrapped_lines.append(truncated_text)
        text = text[length:].lstrip()  # Remove leading space for the next line
    return wrapped_lines


def wrap_multi_line(text, font, max_width):
    """
    Wraps multiple lines of text, taking new lines into account.

    Parameters:
    text (str): The original text to be wrapped.
    font (object): A font object that provides a size method to measure text width.
    max_width (int): The maximum allowable width for the text.

    Returns:
    list: A list of wrapped lines, considering original line breaks.
    """
    lines = text.splitlines()
    wrapped_text = []
    for line in lines:
        wrapped_text.extend(wrap_line(line, font, max_width))
    return wrapped_text


# def wrapline(text, font, maxwidth):
    # done = 0
    # wrapped = []
    # while not done:
        # nl, done, stext = truncline(text, font, maxwidth)
        # wrapped.append(stext.strip())
        # text = text[nl:]
    # return wrapped


# def wrap_multi_line(text, font, maxwidth):
    # """ returns text taking new lines into account.
    # """
    # lines = chain(*(wrapline(line, font, maxwidth) for line in text.splitlines()))
    # return list(lines)


def render_text(font, text, width, color=TEXT_COLOR, justify=-1, antialias=True, dsuu=None, moff=None):
    if moff:
        moffx, moffy = moff
    # Return an image with prettyprinted text.
    lines = wrap_multi_line(text, font, width)

    imgs = [font.render(l, antialias, color) for l in lines]
    h = sum(i.get_height() for i in imgs)
    s = pyv.surface_create((width, h))
    s.fill((0, 0, 0))
    o = 0
    for i in imgs:
        if justify == 0:
            x = width // 2 - i.get_width() // 2
        elif justify > 0:
            x = width - i.get_width()
        else:
            x = 0

        if dsuu:
            dsuu.blit(i, (moffx+x, moffy+o))
        else:
            s.blit(i, (x, o))
        o += i.get_height()

    if moff is None:
        s.set_colorkey((0, 0, 0), pyv.RLEACCEL)
        return s


def draw_text(font, text, rect, color=TEXT_COLOR, justify=-1, antialias=True, dest_surface=None):
    # Draw some text to the screen with the provided options.
    if dest_surface:
        dsu = dest_surface
    else:
        dsu = pyv.get_surface()

    # myimage = render. ...
    render_text(font, text, rect.width, color, justify, antialias, dsuu=dsu, moff=rect.topleft)
    return
    # if justify == 0:
    #     myrect = myimage.get_rect(midtop=rect.midtop)
    # elif justify > 0:
    #     myrect = myimage.get_rect(topleft=rect.topleft)
    # else:
    #     myrect = rect
    # dsu.set_clip(rect)
    # dsu.blit(myimage, myrect)
    # dsu.set_clip(None)


class Image(object):
    def __init__(self, fname=None, frame_width=0, frame_height=0, custom_frames=None,
                 flags=0, color_key=DEFAULT_COLOR_KEY, transparent=False):
        """Load image file, or create blank image, at frame size"""
        if fname:
            self.bitmap = self.get_pre_loaded(fname, transparent)
            if not self.bitmap:
                self.bitmap = pyv.images[fname]
                self.bitmap.set_colorkey(color_key, flags)
        else:
            self.bitmap = pyv.surface_create((frame_width, frame_height))
            self.bitmap.fill(color_key)
            self.bitmap.set_colorkey(color_key, flags)

        self.scrref = pyv.get_surface()

        self.fname = fname
        self.flags = flags
        self.transparent = transparent
        self.color_key = color_key
        if transparent:
            alpha = int(transparent)
            if alpha <= 1:
                alpha = 155
            self.bitmap.set_alpha(alpha)

        if frame_width == 0:
            frame_width = self.bitmap.get_width()
        if frame_height == 0:
            frame_height = self.bitmap.get_height()

        if frame_width > self.bitmap.get_width():
            frame_width = self.bitmap.get_width()
        self.fname = fname
        self.frame_width = frame_width
        self.frame_height = frame_height

        self.custom_frames = custom_frames

    @staticmethod
    def get_pre_loaded(ident, transparent):
        return pre_loaded_images.get((ident, transparent))

    @staticmethod
    def record_pre_loaded(ident, colorset, bitmap, transparent=False):
        pre_loaded_images[(ident, repr(colorset), transparent)] = bitmap

    def _get_frame_area(self, frame):
        if self.custom_frames and frame < len(self.custom_frames):
            area = pyv.new_rect_obj(self.custom_frames[frame])
        else:
            frames_per_row = self.bitmap.get_width() // self.frame_width
            area_x = (frame % frames_per_row) * self.frame_width
            area_y = (frame // frames_per_row) * self.frame_height
            area = pyv.new_rect_obj(area_x, area_y, self.frame_width, self.frame_height)
        return area

    def render(self, dest=(0, 0), frame=0, dest_surface=None ):
        # Render this Image onto the provided surface.
        # Start by determining the correct sub-area of the image.
        area = self._get_frame_area(frame)
        dest_surface = dest_surface or self.scrref  # new way to retrieve the surface used for display

        dest_surface.blit(self.bitmap, dest, area)

    def render_c(self, dest=(0, 0), frame=0, dest_surface=None ):
        # As above, but the dest coordinates point to the center of the image.
        area = self._get_frame_area(frame)

        dest_c = self.get_rect(frame)
        dest_c.center = dest
        dest_surface = dest_surface or pyv.get_surface()  # new way to retrieve the surface used for display

        dest_surface.blit(self.bitmap, dest_c, area)

    def get_subsurface(self, frame):
        # Return one of the frames as a pygame subsurface.
        area = self._get_frame_area(frame)
        return self.bitmap.subsurface(area)

    def get_rect(self, frame):
        # Return a rect of the correct size for this frame.
        if self.custom_frames and frame < len(self.custom_frames):
            return pyv.new_rect_obj(0, 0, self.custom_frames[frame][2], self.custom_frames[frame][3])
        else:
            return pyv.new_rect_obj(0, 0, self.frame_width, self.frame_height)

    def num_frames(self):
        if self.custom_frames:
            return len(self.custom_frames)
        else:
            frames_per_row = self.bitmap.get_width() // self.frame_width
            frames_per_column = self.bitmap.get_height() // self.frame_height
            return frames_per_row * frames_per_column

    def __reduce__(self):
        # Rather than trying to save the bitmap image, just save the parameters.
        return Image, (self.fname, self.frame_width, self.frame_height, self.custom_frames, self.flags,
                       self.color_key, self.transparent)

    def tile(self, dest=None, frame=0, dest_surface=None, x_offset=0, y_offset=0):
        dest_surface = dest_surface or self.scrref  # new way to retrieve the surface used for display

        if not dest:
            dest = dest_surface.get_rect()
        grid_w = dest.w // self.frame_width + 2
        grid_h = dest.h // self.frame_height + 2
        dest_surface.set_clip(dest)
        my_rect = pyv.new_rect_obj(0, 0, 0, 0)

        for x in range(-1, grid_w):
            my_rect.x = dest.x + x * self.frame_width +x_offset
            for y in range(-1, grid_h):
                my_rect.y = dest.y + y * self.frame_height +y_offset
                self.render(my_rect, frame, dest_surface)

        dest_surface.set_clip(None)

    def copy(self,ident=None):
        nu_sprite = Image(frame_height=self.frame_height,frame_width=self.frame_width,)
        nu_sprite.bitmap = self.bitmap.copy()
        if ident:
            self.record_pre_loaded(ident, None, nu_sprite.bitmap)
        return nu_sprite


class TextImage(Image):
    def __init__(self, txt='?????', frame_width=128, color=None, font=None):
        """Create an image of the provided text"""
        if not color:
            color = TEXT_COLOR

        self.txt = txt
        self.bitmap = render_text(font, txt, frame_width, color, justify=0, antialias=False)
        self.frame_width = self.bitmap.get_width()
        self.frame_height = self.bitmap.get_height()
        self.custom_frames = None

    def __reduce__(self):
        # Rather than trying to save the bitmap image, just save the reconstruction details.
        return TextImage, (self.txt, self.frame_width, self.frame_height)


