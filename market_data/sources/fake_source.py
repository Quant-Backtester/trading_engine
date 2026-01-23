from .source import MarketDataSource
from collections.abc import Iterable


class FakeMarketDataSource(MarketDataSource):
    def __init__(self, records):
        self._records: Iterable = records

    def __iter__(self):
        return iter(self._records)
