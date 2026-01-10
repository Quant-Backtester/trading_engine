from .source import MarketDataSource


class FakeMarketDataSource(MarketDataSource):
    def __init__(self, records):
        self._records = records

    def __iter__(self):
        return iter(self._records)
