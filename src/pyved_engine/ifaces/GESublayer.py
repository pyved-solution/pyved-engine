from abc import abstractmethod


# TODO check if its better to have a 'pure' interface
# Step 1: Define an interface (abstract class)
class GESublayer:
    """
    this is used solely to specify the full interface of the Gamedev API

    goal of this CLASS is to define the full engine API for end users...
    But also specialize the API implementation based on the exec. context
    Tom said: in a perfect world the API for the gamedev should be structured ,
     like in FOUR(4) files or parts :

     - I- part
      stores the list of all functions and classes that concretize the API
       (it should be obvious that this file's sole purpose is to select objects from engine_logic, as well as
       objects from highlevel_func and expose them nicely)

     - highlevel_func: implementations that exist at a such high level of abstraction that the ctx doesnt matter

     - context_bridge: basically a container for implementations that can be replaced, based on the ctx
       (->dependency injection pattern)

     - engine_logic: stores the general state of the engine, how the engine transitions from 1 state to another, etc.
       (functions such as init are defined here because they indeed modify the engine state. This file imports the
       two modules mentionned above)
    """
    def __init__(self):
        self.gam_win_size = [0, 0]
        self._stored_lambda = None

    @abstractmethod
    def init(self):  # sublayer/backend initialization
        raise NotImplementedError

    def quit(self):
        raise NotImplementedError  # its basically to flush memory/reset the lower layer state

    @abstractmethod
    def get_pressed(self):
        raise NotImplementedError

    @abstractmethod
    def fire_up_backend(self, user_id: int) -> dict:
        """Fetch user data"""
        raise NotImplementedError

    @abstractmethod
    def draw_circle(self, surface, color_arg, position2d, radius, width):
        raise NotImplementedError

    @abstractmethod
    def draw_line(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def draw_polygon(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def draw_rect(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def init_sound(self):
        raise NotImplementedError

    @abstractmethod
    def sound_quit(self):
        raise NotImplementedError

    @abstractmethod
    def new_font_obj(self, font_src, font_size: int):  # src can be None!
        raise NotImplementedError

    @abstractmethod
    def new_rect_obj(self, *args):  # probably: x, y, w, h
        raise NotImplementedError

    @abstractmethod
    def new_surface_obj(self, size):
        raise NotImplementedError

    @abstractmethod
    def new_clock_obj(self, *args, **kwargs):
        raise NotImplementedError

    def _set_lambda(self, x):
        self.gam_win_size[0] = x * 160
        self.gam_win_size[1] = x * 90  # px
        self._stored_lambda = x

    def _compute_viewport_param_vector(self, new_win_size):
        newval_w, newval_h = new_win_size
        prev_k_factor = 1
        k_candidate = 2
        GWW, GWH = self.gam_win_size
        while (k_candidate * GWW) < newval_w + 1 and (k_candidate * GWH) < newval_h + 1:
            prev_k_factor = k_candidate
            k_candidate += 1
        ups = prev_k_factor
        disp_w, disp_h = new_win_size
        print(f'lambda={self._stored_lambda}; CALC Window {self.gam_win_size}:upscale={ups}')
        widget_s = [ups * GWW, ups * GWH]
        offx, offy = (disp_w - widget_s[0]) // 2, (disp_h - widget_s[1]) // 2
        print('offsets computed:', offx, offy)
        return ups, offx, offy
