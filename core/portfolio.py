from collections.abc import Sequence

from common.enums import Side
from common.types import Percentage, Cash, Price, Timestamp

from dataclasses import dataclass, field

from events.payloads.order_payload import OrderFillPayload, OrderPayload


@dataclass(slots=True)
class TradingMetrics:
    win_rate: Percentage
    profit_factor: float
    avg_win: Cash
    avg_loss: Cash
    win_loss_ratio: float
    avg_holding_period: Timestamp
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_profit: Cash
    total_loss: Cash
    net_profit: Cash
    largest_win: Cash
    largest_loss: Cash
    max_consecutive_wins: int
    max_consecutive_losses: int
    expectancy: Cash
    sharpe_ratio: float | None = None
    max_drawdown: Percentage | None = None


@dataclass(slots=True)
class Portfolio:
    initial_capital: Cash
    current_capital: Cash = field(init=False)
    _trades: list[dict] = field(default_factory=list, init=False)
    _daily_returns: list[float] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.current_capital = self.initial_capital

    def _determine_exit_type(
        self, order: OrderPayload, current_price: Price
    ) -> str:
        if order.take_profit is not None and current_price >= order.take_profit:
            return "take_profit"
        elif order.stop_loss is not None and current_price <= order.stop_loss:
            return "stop_loss"
        return "manual"

    def _calculate_trade_from_order(
        self, order: OrderPayload, current_price: Price
    ) -> dict:
        entry_price = order.price
        exit_price = current_price
        quantity = order.quantity
        commission = 0.0

        if order.side == Side.BUY:
            profit_loss = (exit_price - entry_price) * quantity - commission
        else:
            profit_loss = (entry_price - exit_price) * quantity - commission

        exit_type = self._determine_exit_type(order, exit_price)

        return {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "entry_time": order.timestamp,
            "exit_time": order.timestamp,
            "commission": commission,
            "profit_loss": profit_loss,
            "is_winning": profit_loss > 0,
            "holding_period": 0,
            "exit_type": exit_type,
            "take_profit": order.take_profit,
            "stop_loss": order.stop_loss,
        }

    @property
    def total_trades(self) -> int:
        return len(self._trades)

    @property
    def winning_trades(self) -> list[dict]:
        return [t for t in self._trades if t["is_winning"]]

    @property
    def losing_trades(self) -> list[dict]:
        return [t for t in self._trades if not t["is_winning"]]

    @property
    def take_profit_trades(self) -> list[dict]:
        return [t for t in self._trades if t["exit_type"] == "take_profit"]

    @property
    def stop_loss_trades(self) -> list[dict]:
        return [t for t in self._trades if t["exit_type"] == "stop_loss"]

    @property
    def winning_trades_count(self) -> int:
        return len(self.winning_trades)

    @property
    def losing_trades_count(self) -> int:
        return len(self.losing_trades)

    @property
    def win_rate(self) -> Percentage:
        return (
            (self.winning_trades_count / self.total_trades) * 100
            if self.total_trades > 0
            else 0.0
        )

    @property
    def take_profit_rate(self) -> Percentage:
        tp_trades = len(self.take_profit_trades)
        return (
            (tp_trades / self.total_trades) * 100
            if self.total_trades > 0
            else 0.0
        )

    @property
    def stop_loss_rate(self) -> Percentage:
        sl_trades = len(self.stop_loss_trades)
        return (
            (sl_trades / self.total_trades) * 100
            if self.total_trades > 0
            else 0.0
        )

    @property
    def avg_win(self) -> Cash:
        winning = self.winning_trades
        if not winning:
            return 0.0
        return sum(t["profit_loss"] for t in winning) / len(winning)

    @property
    def avg_loss(self) -> Cash:
        losing = self.losing_trades
        return (
            sum(t["profit_loss"] for t in losing) / len(losing)
            if losing
            else 0.0
        )

    @property
    def avg_take_profit_profit(self) -> Cash:
        tp_trades = self.take_profit_trades
        if not tp_trades:
            return 0.0
        return sum(t["profit_loss"] for t in tp_trades) / len(tp_trades)

    @property
    def avg_stop_loss_loss(self) -> Cash:
        sl_trades = self.stop_loss_trades
        if not sl_trades:
            return 0.0
        return sum(t["profit_loss"] for t in sl_trades) / len(sl_trades)

    @property
    def total_profit(self) -> Cash:
        return sum(t["profit_loss"] for t in self.winning_trades)

    @property
    def total_loss(self) -> Cash:
        return sum(t["profit_loss"] for t in self.losing_trades)

    @property
    def win_loss_ratio(self) -> float:
        if self.avg_loss == 0:
            return 0.0
        return abs(self.avg_win / self.avg_loss) if self.avg_loss != 0 else 0.0

    @property
    def profit_factor(self) -> float:
        gross_profit = sum(t["profit_loss"] for t in self.winning_trades)
        gross_loss = abs(sum(t["profit_loss"] for t in self.losing_trades))
        if gross_loss == 0:
            return float("inf") if gross_profit > 0 else 0.0
        return gross_profit / gross_loss

    @property
    def net_profit(self) -> Cash:
        return self.total_profit + self.total_loss

    @property
    def avg_holding_period(self) -> Timestamp:
        return (
            sum(t["holding_period"] for t in self._trades) // len(self._trades)
            if self._trades
            else 0
        )

    @property
    def largest_win(self) -> Cash:
        return (
            max(t["profit_loss"] for t in self.winning_trades)
            if self.winning_trades
            else 0.0
        )

    @property
    def largest_loss(self) -> Cash:
        return (
            min(t["profit_loss"] for t in self.losing_trades)
            if self.losing_trades
            else 0.0
        )

    @property
    def max_consecutive_wins(self) -> int:
        max_wins = current_wins = 0
        for trade in self._trades:
            if trade["is_winning"]:
                current_wins += 1
                max_wins = max(max_wins, current_wins)
            else:
                current_wins = 0
        return max_wins

    @property
    def max_consecutive_losses(self) -> int:
        max_losses = current_losses = 0
        for trade in self._trades:
            if not trade["is_winning"]:
                current_losses += 1
                max_losses = max(max_losses, current_losses)
            else:
                current_losses = 0
        return max_losses

    @property
    def expectancy(self) -> Cash:
        return self.net_profit / self.total_trades if self.total_trades else 0.0

    @property
    def total_return(self) -> Percentage:
        return (
            (
                (self.current_capital - self.initial_capital)
                / self.initial_capital
            )
            * 100
            if self.initial_capital != 0
            else 0.0
        )

    def add_trade(
        self,
        order: OrderPayload,
        current_price: Price,
        exit_timestamp: Timestamp,
    ) -> None:
        assert order.quantity > 0, "Order must have positive quantity"

        trade = self._calculate_trade_from_order(order, current_price)
        trade["exit_time"] = exit_timestamp
        trade["holding_period"] = exit_timestamp - order.timestamp

        self._trades.append(trade)
        self.current_capital += trade["profit_loss"]

    def add_trades(
        self, trades: list[tuple[OrderPayload, Price, Timestamp]]
    ) -> None:
        for order, current_price, exit_timestamp in trades:
            self.add_trade(order, current_price, exit_timestamp)

    def get_trading_metrics(self) -> TradingMetrics:
        return TradingMetrics(
            win_rate=self.win_rate,
            profit_factor=self.profit_factor,
            avg_win=self.avg_win,
            avg_loss=self.avg_loss,
            win_loss_ratio=self.win_loss_ratio,
            avg_holding_period=self.avg_holding_period,
            total_trades=self.total_trades,
            winning_trades=self.winning_trades_count,
            losing_trades=self.losing_trades_count,
            total_profit=self.total_profit,
            total_loss=self.total_loss,
            net_profit=self.net_profit,
            largest_win=self.largest_win,
            largest_loss=self.largest_loss,
            max_consecutive_wins=self.max_consecutive_wins,
            max_consecutive_losses=self.max_consecutive_losses,
            expectancy=self.expectancy,
        )

    def get_trade_analysis(self) -> dict:
        return {
            "take_profit_trades": len(self.take_profit_trades),
            "stop_loss_trades": len(self.stop_loss_trades),
            "take_profit_rate": self.take_profit_rate,
            "stop_loss_rate": self.stop_loss_rate,
            "avg_take_profit_profit": self.avg_take_profit_profit,
            "avg_stop_loss_loss": self.avg_stop_loss_loss,
            "risk_reward_ratio": abs(
                self.avg_take_profit_profit / self.avg_stop_loss_loss
            )
            if self.avg_stop_loss_loss != 0
            else 0.0,
        }

    def clear(self) -> None:
        self._trades.clear()
        self.current_capital = self.initial_capital
        self._daily_returns.clear()
