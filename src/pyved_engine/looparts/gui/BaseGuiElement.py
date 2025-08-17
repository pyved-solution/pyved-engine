from abc import ABCMeta, abstractmethod
from ... import pe_vars


ANCHOR_LEFT, ANCHOR_RIGHT, ANCHOR_CENTER = range(34151, 34151+3)


class BaseGuiElement(metaclass=ABCMeta):
    """
    Base cls for any Gui element class
    """
    free_gui_id = 821798

    def __init__(self):
        self._id = self.__class__.free_gui_id
        self.__class__.free_gui_id -= 1
        self._parent = None
        self._scrref = vars.screen
        self._debug = 0
        self._abs_pos = [0, 0]
        self._dim = [None, None]
        self._anchor_type = ANCHOR_LEFT
        self._debug = False

        # not all widgets can be de-activated
        self._active = True

    @property
    def active(self):
        return self._active

    def get_abs_rect(self):
        """
        The absolute positioning rect.
        :return: A pygame rect.
        """
        return self._abs_pos[0], self._abs_pos[1], self._dim[0], self._dim[1]

    @abstractmethod
    def get_relative_rect(self):
        """
        The relative positioning rect.
        :return: A pygame rect.
        """

    @abstractmethod
    def set_relative_pos(self, position):
        """
        Method to directly set the relative rect position of an element.
        :param position: The new position to set.
        """

    def get_pos(self):
        """
        getter (takes into account anchoring!)
        :return:
        """
        return self._abs_pos

    def set_position(self, position):
        """
        Method to directly set the absolute screen rect position of an element.
        Warning! This can impact parent container if one is defined
        :param position: The new position to set.
        """
        if not isinstance(position[0], int):
            raise ValueError
        if not isinstance(position[1], int):
            raise ValueError

        self._abs_pos[0], self._abs_pos[1] = position

        if self._parent:
            self._parent.update_pos_from_child(position, self)

    def get_dimensions(self):
        """
        getter
        :return: w, h
        """
        return tuple(self._dim)

    def set_dimensions(self, dimensions):
        """
        setter tho change the dimensions of an element.
        NOTE: Using this on elements inside containers with non-default anchoring arrangements ay make a mess of them.
        :param dimensions: The new dimensions to set.
        """
        self._dim[0], self._dim[1] = dimensions

    def rebuild(self) -> None:
        """
        refresh element/rebuild
        """
        pass

    def update(self, time_delta: float):
        """
        Updates this element's drawable shape, if it has one.
        :param time_delta: The time passed between frames, measured in seconds.
        """
        pass

    @abstractmethod
    def draw(self):
        """
        draw itself
        :return:
        """

    @abstractmethod
    def kill(self):
        """
        Overriding regular sprite kill() method to remove the element from it's container.
        """

    @abstractmethod
    def check_hover(self, time_delta: float, hovered_higher_element: bool) -> bool:
        """
        A method that helps us to determine which, if any, UI Element is currently being hovered
        by the mouse.

        :param time_delta: A float, the time in seconds between the last call to this function
                           and now (roughly).
        :param hovered_higher_element: A boolean, representing whether we have already hovered a
                                       'higher' element.
        :return bool: A boolean that is true if we have hovered a UI element, either just now or
                      before this method.
        """

    @abstractmethod
    def hover_point(self, hover_x: float, hover_y: float) -> bool:
        """
        Test if a given point counts as 'hovering' this UI element. Normally that is a
        straightforward matter of seeing if a point is inside the rectangle. Occasionally it
        will also check if we are in a wider zone around a UI element once it is already active,
        this makes it easier to move scroll bars and the like.

        :param hover_x: The x (horizontal) position of the point.
        :param hover_y: The y (vertical) position of the point.
        :return: Returns True if we are hovering this element.
        """

    @abstractmethod
    def proc_event(self, event) -> bool:
        """
        A stub to override. Gives UI Elements access to pygame events.
        :param event: The event to process.
        :return: Should return True if this element makes use of this event.
        """

    # TODO fix system -> non-compatibility with event sys4

    # def on_hover(self):
    #     """
    #     Can be overriden, called when this UI element first enters the 'hovered' state.
    #     """
    #     pass
    #
    # def on_unhover(self):
    #     """
    #     Can be overriden, called when this UI element leaves the 'hovered' state.
    #     """
    #     pass
    #
    # def on_focus(self):
    #     """
    #     Can be overriden, called when we focus this UI element.
    #     """
    #     pass
    #
    # @abstractmethod
    # def on_unfocus(self):
    #     """
    #     Can be overriden, called when we stop focusing this UI element.
    #     """
    #     pass

    def get_debug_flag(self):
        return self._debug

    def set_debug_flag(self, v=True):
        self._debug = bool(v)

    @abstractmethod
    def set_image(self, new_image):
        """
        Wraps setting the image variable of this element so that we also set the current image
        clip on the image at the same time.
        :param new_image: The new image to set.
        """

    def set_active(self, activate_mode=True):
        """
        tag the widget as active/inactive,
        which determines if the widget will draw itself and process events or not
        """
        self._active = activate_mode

    def set_anchoring(self, anch_code: int):
        """
        Set the current anchoring mode
        :type anch_code: anchoring code (int)
        """
        self._anchor_type = anch_code

    def get_anchoring(self) -> int:
        """
        Get the current anchoring mode that's used by this element so we can position it
        :return: anchoring_code
        """
        return self._anchor_type
