# STL
from collections.abc import Iterator
from pathlib import Path
import csv
from typing import TextIO
from datetime import datetime, timedelta


# Custom
from events.payloads import MarketDataPayload, MarketDataTestPayload
from .source import MarketDataSource


class CSVMarketDataSource(MarketDataSource):
    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._symbol = self._path.stem

    def __iter__(self) -> Iterator[MarketDataPayload]:
        with self._path.open("r", newline="") as file:
            # yield from self._read_csv_file(file=file)
            yield from self._test_read_csv_file(file=file)

    def _read_csv_file(self, file: TextIO) -> Iterator[MarketDataPayload]:
        for row in csv.DictReader(file):
            yield MarketDataPayload(
                symbol=self._symbol,
                price=float(row["price"]),
                volume=int(row["Volume"]),
                timestamp=int(row["timestamp"]),
            )

    def _test_read_csv_file(self, file: TextIO) -> Iterator[MarketDataTestPayload]:
        for row in csv.DictReader(file):
            yield MarketDataTestPayload(
                symbol=self._symbol,
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=int(row["Volume"]),
                timestamp=self.convert_timestamp(row["Date"])
            )

    @staticmethod
    def convert_timestamp(timestamp: str) -> int:
        dt = datetime.strptime(timestamp, "%Y-%m-%d")

        # Convert to YYYYMMDD integer
        date_int = int(dt.strftime("%Y%m%d"))
        return date_int
