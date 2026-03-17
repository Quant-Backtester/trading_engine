from common.types import Percentage, Cash, Timestamp

from dataclasses import dataclass


@dataclass(slots=True)
class Trade:
    entry_price: Cash
    exit_price: Cash
    quantity: float
    entry_time: Timestamp
    exit_time: Timestamp
    commission: Cash = 0.0

    @property
    def profit_loss(self) -> Cash:
        return (
            self.exit_price - self.entry_price
        ) * self.quantity - self.commission

    @property
    def holding_period(self) -> Timestamp:
        return self.exit_time - self.entry_time

    @property
    def is_winning(self) -> bool:
        return self.profit_loss > 0


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


class Portfolio:
    def __init__(self, initial_capital: Cash) -> None:
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self._trades: list[Trade] = []
        self._daily_returns: list[float] = []  # For advanced metrics

    @property
    def total_trades(self) -> int:
        return len(self._trades)

    @property
    def winning_trades(self) -> list[Trade]:
        return [t for t in self._trades if t.is_winning]

    @property
    def losing_trades(self) -> list[Trade]:
        return [t for t in self._trades if not t.is_winning]

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
    def loss_rate(self) -> Percentage:
        return (
            (self.losing_trades_count / self.total_trades) * 100
            if self.total_trades > 0
            else 0.0
        )

    @property
    def avg_win(self) -> Cash:
        winning = self.winning_trades
        if not winning:
            return 0.0
        return (
            sum(t.profit_loss for t in winning) / len(winning)
            if winning
            else 0.0
        )

    @property
    def avg_loss(self) -> Cash:
        losing = self.losing_trades
        return (
            sum(t.profit_loss for t in losing) / len(losing) if losing else 0.0
        )

    @property
    def total_profit(self) -> Cash:
        return sum(t.profit_loss for t in self.winning_trades)

    @property
    def total_loss(self) -> Cash:
        return sum(t.profit_loss for t in self.losing_trades)

    @property
    def win_loss_ratio(self) -> float:
        if self.avg_loss == 0:
            return 0.0
        return abs(self.avg_win / self.avg_loss) if self.avg_loss != 0 else 0.0

    @property
    def profit_factor(self) -> float:
        gross_profit = sum(t.profit_loss for t in self.winning_trades)
        gross_loss = abs(sum(t.profit_loss for t in self.losing_trades))
        if gross_loss == 0:
            return float("inf") if gross_profit > 0 else 0.0
        return gross_profit / gross_loss

    @property
    def net_profit(self) -> Cash:
        return self.total_profit + self.total_loss

    @property
    def avg_holding_period(self) -> Timestamp:
        return (
            sum((t.holding_period for t in self._trades)) // len(self._trades)
            if self._trades
            else 0
        )

    @property
    def largest_win(self) -> Cash:
        return (
            max(t.profit_loss for t in self.winning_trades)
            if self.winning_trades
            else 0.0
        )

    @property
    def largest_loss(self) -> Cash:
        return (
            min(t.profit_loss for t in self.losing_trades)
            if self.losing_trades
            else 0.0
        )

    @property
    def max_consecutive_wins(self) -> int:
        max_wins = current_wins = 0
        for trade in self._trades:
            if trade.is_winning:
                current_wins += 1
                max_wins = max(max_wins, current_wins)
            else:
                current_wins = 0
        return max_wins

    @property
    def max_consecutive_losses(self) -> int:
        max_losses = current_losses = 0
        for trade in self._trades:
            if not trade.is_winning:
                current_losses += 1
                max_losses = max(max_losses, current_losses)
            else:
                current_losses = 0
        return max_losses

    @property
    def expectancy(self) -> Cash:
        """Expected profit per trade"""
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

    def add_trade(self, trade: Trade) -> None:
        self._trades.append(trade)
        self.current_capital += trade.profit_loss

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
