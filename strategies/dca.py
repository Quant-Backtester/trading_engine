from .strategy import Strategy
from .strategy_enum import StrategyEnum
from common.types import Quantity, Symbol


class DCA(Strategy):
    def __init__(self, buyframe: int, buy_amount: Quantity, symbol: Symbol) -> None:
        self._buyframe = buyframe
        self._symbol = symbol

    @property
    def strategy_id(self) -> StrategyEnum:
        return StrategyEnum.DCA


