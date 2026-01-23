# STL
from typing import Protocol
from collections.abc import Iterator
from abc import abstractmethod

# Custom
from events.payloads import MarketDataPayload


class MarketDataSource(Protocol):
    @abstractmethod
    def __iter__(self) -> Iterator[MarketDataPayload]: ...

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

    def __repr__(self) -> str:
        return f"{self.__class__}"
