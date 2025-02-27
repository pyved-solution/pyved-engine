from .GESublayer import GESublayer


# Step 2: Implement the interface in a concrete class
class PygameWrapper(GESublayer):
    def __init__(self):
        import pygame

        # let's avoid AT ALL COSTS to make this public, otherwise using the wrapper has no meaning
        self._pygame = pygame

        self.PixelArray = self._pygame.PixelArray  # required by jetpack carverns
        self.sprite = self._pygame.sprite
        # Objectifier({
        #     'Sprite': self._pygame.sprite.Sprite,
        #     'Group': self._pygame.sprite.Group,
        #     'spritecollide': self._pygame.sprite.spritecollide
        # })
        self.event = self._pygame.event
        self.display = self._pygame.display
        self.mixer = self._pygame.mixer
        self.time = self._pygame.time
        self.Surface = self._pygame.Surface
        self.transform = self._pygame.transform
        self.image = self._pygame.image

        # self.key = self._pygame.key
        self.mouse = self._pygame.mouse

        # copy many pygame constants
        self.SRCALPHA = self._pygame.SRCALPHA
        self.RLEACCEL = self._pygame.RLEACCEL
        self.QUIT = self._pygame.QUIT
        self.KEYDOWN = self._pygame.KEYDOWN
        self.KEYUP = self._pygame.KEYUP
        self.MOUSEBUTTONDOWN = self._pygame.MOUSEBUTTONDOWN
        self.MOUSEBUTTONUP = self._pygame.MOUSEBUTTONUP

        # -----------------------------
        # key codes
        # -----------------------------
        self.K_ESCAPE = self._pygame.K_ESCAPE
        self.K_BACKSPACE = self._pygame.K_BACKSPACE
        self.K_RETURN = self._pygame.K_RETURN
        self.K_SPACE = self._pygame.K_SPACE
        self.K_UP = self._pygame.K_UP
        self.K_LEFT = self._pygame.K_LEFT
        self.K_DOWN = self._pygame.K_DOWN
        self.K_RIGHT = self._pygame.K_RIGHT

    def get_pressed(self):
        return self._pygame.key.get_pressed()

    def set_mode(self, *args, **kwargs):
        self._pygame.display.set_mode(args[0])  # pass size only

    def new_surface_obj(self, size):
        return self._pygame.surface.Surface(size)

    def new_clock_obj(self, *args, **kwargs):
        return self._pygame.time.Clock()

    def init(self):
        self._pygame.init()

    def init_sound(self):
        self._pygame.mixer.init()

    def sound_quit(self):
        self._pygame.mixer.quit()

    def set_caption(self, txt: str, icon_title=''):
        self._pygame.display.set_caption(txt, icon_title)

    def quit(self):
        self._pygame.quit()

    def image_load(self, fileobj_or_path, *args):
        if len(args) > 0:
            return self._pygame.image.load(fileobj_or_path, namehint=args[0])
        return self._pygame.image.load(fileobj_or_path)

    def draw_circle(self, surface, color_arg, position2d, radius, width):
        self._pygame.draw.circle(surface, color_arg, position2d, radius, width)

    def fire_up_backend(self, user_id: int) -> dict:
        # Example: Fetch data from a REST API
        return {"user_id": user_id, "name": "Bob", "role": "User"}

    def draw_line(self, *args, **kwargs):
        self._pygame.draw.line(*args, **kwargs)

    def draw_rect(self, *args, **kwargs):
        self._pygame.draw.rect(*args, **kwargs)

    def draw_polygon(self, *args, **kwargs):
        self._pygame.draw.polygon(*args, **kwargs)

    def new_font_obj(self, font_src, font_size: int):  # src can be None!
        return self._pygame.font.Font(font_src, font_size)

    def new_rect_obj(self, *args):  # probably: x, y, w, h
        return self._pygame.Rect(*args)

# class WebGlBackendBridge(GameEngineSublayer):
#     def fire_up_backend(self, user_id: int) -> dict:
#         # Example: Fetch data from MySQL
#         return {"user_id": user_id, "name": "Alice", "role": "Admin"}
