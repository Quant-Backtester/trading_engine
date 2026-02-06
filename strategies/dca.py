from .strategy import Strategy
from .strategy_enum import StrategyEnum


class DCA(Strategy):
    def __init__(self, buyframe: int) -> None:
        pass

    @property
    def strategy_id(self) -> StrategyEnum:
        return StrategyEnum.DCA
