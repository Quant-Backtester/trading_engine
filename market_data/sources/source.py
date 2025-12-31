# STL
from typing import Iterator, Protocol

# Custom
from events.payloads import MarketDataPayload


class MarketDataSource(Protocol):
    def __iter__(self) -> Iterator[MarketDataPayload]:
        ...
