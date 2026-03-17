from events.event import Event
from events.payloads.market_payload import MarketDataPayload
from strategies.signal import AddSignal, NullSignal, Signal
from common.enums import OrderType, Side

from .strategy import Strategy
from .strategy_enum import StrategyEnum
from common.types import Quantity, Symbol


class DCA(Strategy):
    def __init__(self, buyframe: int, buy_amount: Quantity) -> None:
        super().__init__()
        self._buyframe = buyframe
        self._buy_amount = buy_amount
        self._last_buy_time: int | None = None

    @property
    def strategy_id(self) -> StrategyEnum:
        return StrategyEnum.DCA

    def on_event(self, event: Event) -> Signal:
        currnet_time = event.timestamp

        if self._should_buy(currnet_time) and isinstance(event.payload, MarketDataPayload):
            return AddSignal(side=Side.BUY, type =OrderType.MARKET ,price=event.payload.price)

        return NullSignal


    def _should_buy(self, current_timestamp: int) -> bool:
        if self._last_buy_time is None:
            return True

        # Simple integer comparison
        time_since_last_buy = current_timestamp - self._last_buy_time
        return time_since_last_buy >= self._buyframe

    def get_next_buy_time(self) -> int | None:

        if self._last_buy_time is None:
            return None
        return self._last_buy_time + self._buyframe


    def reset(self) -> None:
        self._last_buy_time = None