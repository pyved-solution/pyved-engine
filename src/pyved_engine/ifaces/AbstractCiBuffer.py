from abc import ABC, abstractmethod


class AbstractCiBuffer(ABC):
    """
    Interface for a circular buffer.

    Any implementation must provide the following methods:
      - init(gmax_len: int = 128) -> None: Initializes the buffer with an optional maximum length.
      - get_size() -> int: Returns the current number of elements in the buffer.
      - is_empty() -> bool: Checks if the buffer is empty.
      - is_full() -> bool: Checks if the buffer is full.
      - enqueue(item) -> None: Adds an item to the buffer.
      - dequeue(): Removes and returns the oldest item from the buffer.
      - front(): Returns the oldest item without removing it.
    """

    @abstractmethod
    def init(self, gmax_len: int = 128) -> None:
        """
        Initialize the CircularBuffer with an optional maximum length.
        """
        pass

    @abstractmethod
    def get_size(self) -> int:
        """
        Return the number of elements currently in the CircularBuffer.
        """
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        """
        Return True if the CircularBuffer is empty, otherwise False.
        """
        pass

    @abstractmethod
    def is_full(self) -> bool:
        """
        Return True if the CircularBuffer is full, otherwise False.
        """
        pass

    @abstractmethod
    def enqueue(self, item) -> None:
        """
        Insert an item at the back of the CircularBuffer.
        """
        pass

    @abstractmethod
    def dequeue(self):
        """
        Remove and return the item at the front of the CircularBuffer.

        Raises:
            IndexError: If the CircularBuffer is empty.
        """
        pass

    @abstractmethod
    def front(self):
        """
        Return the item at the front of the CircularBuffer without removing it.

        Raises:
            IndexError: If the CircularBuffer is empty.
        """
        pass
