# STL
from typing import Protocol
from collections.abc import Iterator

# Custom
from events.payloads import MarketDataPayload


class MarketDataSource(Protocol):
    def __iter__(self) -> Iterator[MarketDataPayload]:
        ...


__all__ = (
    "MarketDataSource",
)