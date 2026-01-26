# STL
from collections.abc import MutableMapping
from dataclasses import dataclass

# Custom
from common.types import Cash, OrderId, Price, Symbol, Quantity, Percentage
from .position_manager import PositionManager
from events.payloads import OrderSubmitPayload, OrderPayload, OrderFillPayload
from common.enums import Side


type Openings = MutableMapping[OrderId, OrderSubmitPayload]

@dataclass(slots=True)
class PortfolioMetrics:
    total_return: Cash
    max_drawdown: Cash
    sharpe_ratio: Percentage
    win_rate: Percentage
    profit_factor: Percentage
    sortino_ratio: Percentage
    calmar_ratio: Percentage


class Portfolio:
    def __init__(self, initial_cash: Cash) -> None:
        self._position_manager = PositionManager(initial_cash=initial_cash)
        self.initial_capital = initial_cash
        self.drawdown_series: list[float] = []
        self.daily_returns: list[float] = []
        self.metrics = None

    




    @property
    def total_pnl(self) -> Cash:
        return (
            self._position_manager.realized_pnl +
            self._position_manager.total_unrealized_pnl
        )