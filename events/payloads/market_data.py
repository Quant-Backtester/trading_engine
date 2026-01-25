
from dataclasses import dataclass

from common.types import Price, Symbol, Timestamp, Volume


# technically this is the one for a more rigorous backtesting engine as OJLC shouldn't be known ahead of time
@dataclass(frozen=True, slots=True)
class MarketDataPayload:
    timestamp: Timestamp
    symbol: Symbol
    price: Price
    volume: Volume


@dataclass(frozen=True, slots=True)
class MarketDataTestPayload:
    symbol: Symbol
    open: Price
    high: Price
    low: Price
    close: Price
    volume: Volume
    timestamp: Timestamp


