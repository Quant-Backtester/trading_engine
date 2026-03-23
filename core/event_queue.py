# STL
import heapq
from typing import NamedTuple

# Custom
from events.event import Event


class Entry(NamedTuple):
    sequence: int
    event: Event


class EventQueue:
    __slots__ = "_heap", "_sequence"

    def __init__(self) -> None:
        self._heap: list[Entry] = []
        self._sequence: int = 0

    @property
    def sequence_number(self) -> int:
        return self._sequence

    @sequence_number.setter
    def sequence_number(self) -> None:
        raise AttributeError("sequence_number is read only")

    @sequence_number.deleter
    def sequence_number(self) -> None:
        raise AttributeError("sequence_number cannot be deleted")

    def push(self, event: Event) -> None:
        entry = Entry(sequence=self._sequence, event=event)
        heapq.heappush(self._heap, entry)
        self._sequence += 1

    def check_empty(self) -> bool:
        if not self._heap:
            return True
        return False

    def pop(self) -> Event:
        if self.check_empty():
            raise IndexError("Empty EventQueue")

        entry = heapq.heappop(self._heap)

        return entry.event

    def peek(self) -> Event:
        if self.check_empty():
            raise IndexError("empty EventQueue")
        return self._heap[0].event

    def __len__(self) -> int:
        return len(self._heap)

    def clear(self) -> None:
        self._heap.clear()
