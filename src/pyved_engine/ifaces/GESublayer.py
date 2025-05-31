from abc import ABC, abstractmethod


# Step 1: Define an interface (abstract class)
class GESublayer(ABC):
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
    @abstractmethod
    def init(self):  # sublayer/backend initialization
        pass

    def quit(self):
        pass  # its basically to flush memory/reset the lower layer state

    @abstractmethod
    def get_pressed(self):
        pass

    @abstractmethod
    def fire_up_backend(self, user_id: int) -> dict:
        """Fetch user data"""
        pass

    @abstractmethod
    def draw_circle(self, surface, color_arg, position2d, radius, width):
        pass

    @abstractmethod
    def draw_line(self, *args, **kwargs):
        pass

    @abstractmethod
    def draw_polygon(self, *args, **kwargs):
        pass

    @abstractmethod
    def draw_rect(self, *args, **kwargs):
        pass

    @abstractmethod
    def init_sound(self):
        pass

    @abstractmethod
    def sound_quit(self):
        pass

    @abstractmethod
    def new_font_obj(self, font_src, font_size: int):  # src can be None!
        pass

    @abstractmethod
    def new_rect_obj(self, *args):  # probably: x, y, w, h
        pass

    @abstractmethod
    def new_surface_obj(self, size):
        pass

    @abstractmethod
    def new_clock_obj(self, *args, **kwargs):
        pass
