"""
Licensed code LGPL 3
the KataGames.io company (c) 2021-2025

TL;DR - Pyved isnt using 100% of pygame functions. So... How much of pygame do we use?

Thanks to the current file, I can:
(A) specify a SUBSET of pygame

(B) offer a formal interface for the so-called "PRIMAL backend". Such a backend can
be implemented in various ways. Interestingly, one possible way is to use a SUBSET of pygame.
Since I consider that it wouldn't be great to use a subset of pygame without "exposing" it
to the end-user too (pygame is a nice tool, after all)
it is decided that the subset used is equal to the one I specified in A.

Having a formal interface is important as it enables me to "plug" into a different system/
another software environment. Components like KENGI, the KataSDK, etc. need to be
adaptive because at the end of the day, we wish to execute games in a browser.
"""
from abc import ABC, abstractmethod


class DeepEvSource(ABC):
    @abstractmethod
    def fetch_raw_events(self):
        pass

    @abstractmethod
    def joystick_init(self, idj):
        pass

    @abstractmethod
    def joystick_info(self, idj):
        pass

    @abstractmethod
    def joystick_count(self):
        pass
