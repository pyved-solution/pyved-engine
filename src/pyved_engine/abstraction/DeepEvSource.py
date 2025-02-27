"""
Licensed code LGPL 3
(c) 2018-2024, to the Kata.Games company

TL;DR - Pyved is not using 100% of pygame functions.
So how much of pygame do we use?

More precisely: this file is here so I can:
(A) specify (for this I propose an informal interface) a SUBSET of pygame

(B) offer a formal interface for the so-called "PRIMAL backend". Such a backend can
be implemented in various ways. Interestingly, one possible way is to use a SUBSET of pygame.
Since I consider that it wouldn't be great to use a subset of pygame without "exposing" it
to the end-user too (pygame is a nice tool, after all)
it is decided that the subset used is equal to the one I specified in A.

Having a formal interface is important as it enables me to "plug" into a different system/
another software environment. Components like KENGI, the KataSDK, etc. need to be
adaptive because at the end of the day, we wish to execute games in a browser.
"""
from abc import abstractmethod, ABCMeta


class DeepEvSource(metaclass=ABCMeta):
    @abstractmethod
    def fetch_kengi_events(self):
        raise NotImplementedError

    @abstractmethod
    def joystick_init(self, idj):
        raise NotImplementedError

    @abstractmethod
    def joystick_info(self, idj):
        raise NotImplementedError

    @abstractmethod
    def joystick_count(self):
        raise NotImplementedError
