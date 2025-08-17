from ..ifaces.AbstractCiBuffer import AbstractCiBuffer
from collections import deque


class CircularBuffer(AbstractCiBuffer):
    # implementation of the circular buffer fully based on collections.deque

    def init(self, gmax_len=128):
        """
        Initialize the CircularBuffer with a gmax_len if given. Default size is 128
        """
        self.deque_obj = deque(maxlen=gmax_len)

    def __str__(self):
        """Return a formatted string representation of this CircularBuffer."""
        items = ['{!r}'.format(item) for item in self.deque_obj]
        return '[' + ', '.join(items) + ']'

    def get_size(self):
        return len(self.deque_obj)

    def is_empty(self):
        """Return True if the head of the CircularBuffer is equal to the tail,
        otherwise return False"""
        return len(self.deque_obj) == 0

    def is_full(self):
        """Return True if the tail of the CircularBuffer is one before the head,
        otherwise return False"""
        return len(self.deque_obj) == self.deque_obj.maxlen

    def enqueue(self, item):
        """Insert an item at the back of the CircularBuffer
        Runtime: O(1) Space: O(1)"""
        self.deque_obj.append(item)

    def dequeue(self):
        """Return the item at the front of the Circular Buffer and remove it
        Runtime: O(1) Space: O(1)"""
        return self.deque_obj.popleft()

    def front(self):
        """Return the item at the front of the CircularBuffer
        Runtime: O(1) Space: O(1)"""
        if len(self.deque_obj):
            return self.deque_obj[len(self.deque_obj) - 1]
        raise IndexError('circular buffer is currently empty!')
