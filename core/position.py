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

        calculate_unrealized_pnl = (
            lambda quantity, last_price, avg_price: quantity
            * (last_price - avg_price)
        )

        return calculate_unrealized_pnl(
            quantity=self.quantity,
            last_price=self.last_price,
            avg_price=self.avg_price,
        )

    @property
    def change_in_percentage(self) -> Percentage:
        if (
            self.quantity == 0
            or self.last_price is None
            or self.avg_price == 0.0
        ):
            return 0.0

        calculate_percentage = lambda x, y: (x - y) / y

        return calculate_percentage(x=self.last_price, y=self.avg_price)
