from .source import MarketDataSource


class FakeMarketDataSource:
    def __init__(self, records):
        self._records = records

    def __iter__(self):
        return iter(self._records)
