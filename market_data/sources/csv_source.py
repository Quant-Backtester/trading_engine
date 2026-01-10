# STL
from collections.abc import Iterator
from pathlib import Path
import csv
from typing import TextIO


# Custom
from events.payloads import MarketDataPayload
from .source import MarketDataSource


class CSVMarketDataSource(MarketDataSource):
    def __init__(self, path: str) -> None:
        self._path = Path(path)

    def __iter__(self) -> Iterator[MarketDataPayload]:
        with self._path.open("r", newline="") as f:
            yield from self._read_csv_file(file=f)

    @staticmethod
    def _read_csv_file(file: TextIO) -> Iterator[MarketDataPayload]:
        for row in csv.DictReader(file):
            yield MarketDataPayload(
                symbol=row["symbol"],
                price=float(row["price"]),
                volume=int(row["volume"]),
                timestamp=int(row["timestamp"]),
            )
