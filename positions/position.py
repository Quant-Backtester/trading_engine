from dataclasses import dataclass

#Cusotm
from common.types import Symbol, Quantity, Price

@dataclass(slots=True)
class Position:
    symbol: Symbol
    quantity: Quantity = 0
    avg_price : Price = 0.0