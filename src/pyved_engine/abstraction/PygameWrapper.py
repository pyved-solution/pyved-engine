from ..ifaces.GESublayer import GESublayer


class PygameWrapper(GESublayer):
    """
    (Step 2) Implementing the GESublayer interface, via a concrete pygame-based class
    """
    def __init__(self):
        super().__init__()
        # manage upscaling etc
        self.stored_size = [0, 0]
        self._is_scr_init = False
        self.gam_win_size = [0, 0]
        self.stored_upscaling = None  # when not init, afterwards it can never be None
        self.ref_realscreen = None
        self.gfx_offsets = [0, 0]
        self._upscaling_val = None
        self._vsurface = None
        self._vsurface_required = False
        self.fullscreen_flag = False

        self.first_fullscreen_change = True

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
        self.USEREVENT = self._pygame.USEREVENT

        self.SRCALPHA = self._pygame.SRCALPHA
        self.RLEACCEL = self._pygame.RLEACCEL
        self.VIDEORESIZE = self._pygame.VIDEORESIZE
        self.FULLSCREEN = self._pygame.FULLSCREEN
        self.RESIZABLE = self._pygame.RESIZABLE

        # STOP using these as we create a higher-level of abstraction event system,
        # see EngineEvTypes
        # self.QUIT = self._pygame.QUIT
        # self.KEYDOWN = self._pygame.KEYDOWN
        # self.KEYUP = self._pygame.KEYUP
        # self.MOUSEBUTTONDOWN = self._pygame.MOUSEBUTTONDOWN
        # self.MOUSEBUTTONUP = self._pygame.MOUSEBUTTONUP
        # self.MOUSEMOTION = self._pygame.MOUSEMOTION

        # -----------------------------
        # key codes
        # -----------------------------
        self.K_ESCAPE = self._pygame.K_ESCAPE
        self.K_BACKSPACE = self._pygame.K_BACKSPACE
        self.K_RETURN = self._pygame.K_RETURN
        self.K_SPACE = self._pygame.K_SPACE
        # key arrows
        self.K_UP = self._pygame.K_UP
        self.K_LEFT = self._pygame.K_LEFT
        self.K_DOWN = self._pygame.K_DOWN
        self.K_RIGHT = self._pygame.K_RIGHT
        # letters
        self.K_a = self._pygame.K_a
        self.K_b = self._pygame.K_b
        self.K_c = self._pygame.K_c
        self.K_d = self._pygame.K_d
        self.K_e = self._pygame.K_e
        self.K_f = self._pygame.K_f
        self.K_g = self._pygame.K_g
        self.K_h = self._pygame.K_h
        self.K_i = self._pygame.K_i
        self.K_j = self._pygame.K_j
        self.K_k = self._pygame.K_k
        self.K_l = self._pygame.K_l
        self.K_m = self._pygame.K_m
        self.K_n = self._pygame.K_n
        self.K_o = self._pygame.K_o
        self.K_p = self._pygame.K_p
        self.K_q = self._pygame.K_q
        self.K_r = self._pygame.K_r
        self.K_s = self._pygame.K_s
        self.K_t = self._pygame.K_t
        self.K_u = self._pygame.K_u
        self.K_v = self._pygame.K_v
        self.K_w = self._pygame.K_w
        self.K_x = self._pygame.K_x
        self.K_y = self._pygame.K_y
        self.K_z = self._pygame.K_z

        self.K_F11 = self._pygame.K_F11

    def get_pressed(self):
        return self._pygame.key.get_pressed()

    def new_surface_obj(self, size):
        return self._pygame.surface.Surface(size)

    def surface_transform(self, s1, new_size, dest=None):
        if dest:
            r = self._pygame.transform.scale(s1, new_size, dest)
        else:
            r = self._pygame.transform.scale(s1, new_size)
        return r

    def get_window_size(self):
        return self._pygame.display.get_surface().get_size()

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

    def fire_up_backend(self, user_id: int):
        # Example: Fetch data from a REST API
        # return {"user_id": user_id, "name": "Bob", "role": "User"}
        self._pygame.display.set_mode((640, 480), self.RESIZABLE)  # no need to pass a realistic resolution now

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

    # ------------------------------------------
    #  below: everything related to Gfx and letterboxing
    # ------------------------------------------
    def proj_to_vscreen(self, xy_pair):
        usf = self._upscaling_val
        a, b = xy_pair
        x, y = a - self.gfx_offsets[0], b - self.gfx_offsets[1]
        if usf != 1:
            return x // usf, y // usf
        return x, y

    def set_upscaling(self, new_upscal_val):
        if int(self._upscaling_val) != new_upscal_val:
            self._upscaling_val = int(new_upscal_val)
            self._vsurface_required = True

    def get_upscaling(self):
        return self._upscaling_val

    def vscreen_flip(self):
        usf = self.get_upscaling()
        if usf == 1:
            self.ref_realscreen.blit(self._vsurface, self.gfx_offsets)
        else:
            target_size = (usf * self.gam_win_size[0], usf * self.gam_win_size[1])
            # coded at the sublayer level
            new_surf = self.transform.scale(
                self._vsurface, target_size
            )
            self.ref_realscreen.blit(new_surf, self.gfx_offsets)
        self.display.update()

    def do_screen_param(self, lambda_factor, total_disp_size, cached_paintev):
        """
        :param lambda_factor: in the range 1-4. Multiplier applied to 160x90 to comptute the game window (no upscaling)
        :param total_disp_size: how many pixels available on the screen e.g. 1920x1080
        :param cached_paintev: can be None or a pyved event that needs to have its .screen attribute set

        :returns:surface on which to draw
        """
        if not isinstance(lambda_factor, int):
            raise ValueError('invalid lamda factor!')
        if self._is_scr_init:
            raise RuntimeError('cannot init screen more than once!')

        # ensure screen is ready to do drawings
        self.ref_realscreen = self.display.get_surface()
        assert self.ref_realscreen is not None
        assert total_disp_size == self.ref_realscreen.get_size()
        self._is_scr_init = True

        self._set_lambda(lambda_factor)
        self.adapt_window_size(total_disp_size)
        self._vsurface = vsurf = self.new_surface_obj(self.gam_win_size)
        if vsurf is None:
            raise ValueError(
                'something\'s really off with screen surface initialization (vscreen.do_screen_param func)')

        if cached_paintev:
            cached_paintev.screen = vsurf
        return vsurf

    def adapt_window_size(self, new_w_size):
        y, offx, offy = self._compute_viewport_param_vector(new_w_size)  # returns drawing size w,h then the upscaling

        self._upscaling_val = y
        self.gfx_offsets[0] = offx
        self.gfx_offsets[1] = offy
        # via la ligne ci-dessous,
        # VOLONTAIREMENT, je casse le centrage, pour que ce soit plus simple d'obtenir le résulat equivalent au Local,
        # mais dans le WebCtx (simplification BIENVENUE, dans un 1er temps...)
        self.gfx_offsets = [0, 0]
        # -----------------------

    def is_fullscreen(self):
        return self.fullscreen_flag

    def exit_fullscreen(self):
        print('fullscreen (pygamewrappen): OFF')
        self.fullscreen_flag = False
        self.ref_realscreen = self.display.set_mode(self.stored_size, self._pygame.RESIZABLE)
        #self.ref_realscreen.fill('black')
        self._vsurface.fill('black')
        # resize logic will be called after a .resize event has been raised
        #self.adapt_window_size(self.stored_size)

    def enter_fullscreen(self):
        print('fullscreen (pygamewrappen): ON')
        self.fullscreen_flag = True
        self.stored_size = self.ref_realscreen.get_size()
        self.ref_realscreen = d = self.display.set_mode((0, 0), self._pygame.FULLSCREEN)
        #self.ref_realscreen.fill('black')
        if self.first_fullscreen_change:  # pygame quirks: why the .RESIZE event is not sent the first time? no idea
            self.adapt_window_size(d.get_size())
        self.first_fullscreen_change = False

# class WebGlBackendBridge(GameEngineSublayer):
#     def fire_up_backend(self, user_id: int) -> dict:
#         # Example: Fetch data from MySQL
#         return {"user_id": user_id, "name": "Alice", "role": "Admin"}
