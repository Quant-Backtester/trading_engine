# STL
from dataclasses import dataclass

# Cusotm
from common.types import Symbol, Quantity, Price, Cash, Percentage


@dataclass(slots=True)
class Position:
    symbol: Symbol
    quantity: Quantity = 0
    avg_price: Price = 0.0
    last_price: Price | None = None

    @property
    def unrealized_pnl(self) -> Cash:
        if self.quantity == 0 or self.last_price is None:
            return 0.0
        return self.quantity * (self.last_price - self.avg_price)

    @property
    def change_in_percentage(self) -> Percentage:
        if (
            self.quantity == 0
            or self.last_price is None
            or self.avg_price == 0.0
        ):
            return 0.0
        return (self.last_price - self.avg_price) // self.avg_price

