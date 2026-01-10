# STL
from typing import Protocol
from collections.abc import Iterator
from abc import abstractmethod

# Custom
from events.payloads import MarketDataPayload


class MarketDataSource(Protocol):
    @abstractmethod
    def __iter__(self) -> Iterator[MarketDataPayload]: ...
