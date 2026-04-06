
from common.enums import OrderType, Side
from common.types import Price, Quantity
from events.event import Event
from events.payloads.market_payload import MarketDataPayload
from strategies.signal import AddSignal, NullSignal, Signal
from strategies.strategy import Strategy

class EDCA(Strategy):
    def __init__(
        self,
        base_amount: Quantity,
        adjustment_amount: Quantity,
        buy_frequency: int = 1,
        lookback_periods: int = 1
    ) -> None:
        self._base_amount: Quantity = base_amount
        self._adjustment_amount: Quantity = adjustment_amount
        self._buy_frequency: int = buy_frequency
        self._lookback_periods: int = lookback_periods
        self._last_buy_time: int | None = None
        self._last_price: Price | None = None
        self._period_returns: list[float] = []
        self._next_amount: Quantity = base_amount
        self._events_since_last_buy: int = 0
        self._period_prices: list[Price] = []

    def get_hash_key(self) -> tuple[object, ...]:
        return (self._base_amount, self._adjustment_amount, self._buy_frequency, self._lookback_periods)

    def _calculate_period_return(self, current_price: Price, previous_price: Price) -> float:
        return (current_price - previous_price) / previous_price

    def _determine_next_amount(self) -> Quantity:
        if not self._period_returns:
            return self._base_amount

        last_return = self._period_returns[-1]

        if last_return < 0:
            return self._next_amount + self._adjustment_amount
        elif last_return > 0:
            return max(self._next_amount - self._adjustment_amount, 0)
        else:
            return self._next_amount

    def _should_buy(self) -> bool:
        if self._last_buy_time is None:
            return True

        self._events_since_last_buy += 1

        if self._events_since_last_buy >= self._buy_frequency:
            self._events_since_last_buy = 0
            return True

        return False

    def _track_period_return(self, current_price: Price) -> None:
        self._period_prices.append(current_price)

        if len(self._period_prices) > self._lookback_periods + 1:
            self._period_prices.pop(0)

        if len(self._period_prices) >= 2:
            previous_price = self._period_prices[0]
            period_return = self._calculate_period_return(current_price, previous_price)

            if len(self._period_returns) >= self._lookback_periods:
                self._period_returns.pop(0)
            self._period_returns.append(period_return)

    def on_event(self, event: Event) -> Signal:
        if isinstance(event.payload, MarketDataPayload):
            self._track_period_return(event.payload.price)

            if self._period_returns:
                self._next_amount = self._determine_next_amount()

            if self._should_buy():
                self._last_buy_time = event.timestamp
                investment_amount = self._next_amount
                self._next_amount = self._base_amount

                return AddSignal(
                    side=Side.BUY,
                    type=OrderType.MARKET,
                    price=event.payload.price,
                    symbol=event.payload.symbol,
                    quantity=investment_amount,
                )

        return NullSignal()

    def get_next_investment_amount(self) -> Quantity:
        return self._next_amount

    def get_period_returns(self) -> list[float]:
        return self._period_returns.copy()

    def reset(self) -> None:
        self._last_buy_time = None
        self._last_price = None
        self._period_returns.clear()
        self._period_prices.clear()
        self._next_amount = self._base_amount
        self._events_since_last_buy = 0