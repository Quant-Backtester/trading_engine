
from dataclasses import dataclass

from common.types import Price, Symbol, Timestamp, Volume


@dataclass(frozen=True, slots=True)
class MarketDataPayload:
    timestamp: Timestamp
    symbol: Symbol
    price: Price
    volume: Volume