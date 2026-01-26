# STL
from typing import Protocol
from collections.abc import Iterator

# Custom
from events.payloads import MarketData

class SourceReprMixin:
    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f"<{self.__class__}>"


class MarketDataSource[T: MarketData](Protocol):
    def __iter__(self) -> Iterator[T]: ...
