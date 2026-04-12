# STL
import logging

# Custom
from core.strategy_handler import StrategyHandler
from events.event import Event, MarketDataEvent, OrderFillEvent, TimerEvent
from events.event_dispatcher import EventDispatcher
from .clock import Clock
from .event_queue import EventQueue
from .portfolio import Portfolio
from .order_manager import OrderManager
from .position_manager import PositionManager
from strategies import Strategy
from common.types import Cash

logger: logging.Logger = logging.getLogger("engine")


class Engine:
    __slots__ = (
        "_queue",
        "_clock",
        "_strategy_handler",
        "_portfolio",
        "_orderManager",
        "_positionManager",
        "_event_dispatcher",
        "_initial_cash",
    )

    def __init__(self, initial_cash: Cash = 100000) -> None:
        self._initial_cash = initial_cash
        self._setup()
        logger.info("engine setup successfully")

    def _setup(self) -> None:
        self._queue: EventQueue = EventQueue()
        self._clock: Clock = Clock()
        self._strategy_handler = StrategyHandler()
        self._portfolio = Portfolio(initial_capital=self._initial_cash)
        self._orderManager = OrderManager()
        self._positionManager = PositionManager(_cash=self._initial_cash)
        self._event_dispatcher = EventDispatcher()
        self.add_event_handlers()

    def add_event_handlers(self) -> None:
        self._event_dispatcher.register(
            MarketDataEvent, self._fill_submitted_orders
        )
        self._event_dispatcher.register(
            event_type=MarketDataEvent, callback=self._close_trades
        )

    def add_strategy(self, strategy: Strategy) -> bool:
        if state := self._strategy_handler.add_strategy(strategy=strategy):
            logger.info("added strategy: %s", strategy)
            return state
        logger.info("failed to add strategy: %s", strategy)
        return state

    def reset(self) -> None:
        self._setup()
        logger.info("reset sucessfully")

    def push_event(self, event: Event) -> None:
        self._queue.push(event=event)

    def run(self) -> None:
        logger.info("engine started running")
        while len(self._queue) > 0:
            event: MarketDataEvent | OrderFillEvent | TimerEvent = (
                self._queue.pop()
            )
            logger.info(
                "Dispatching event: type=%s ts=%d", event, event.timestamp
            )

            self._clock.advance_to(timestamp=event.timestamp)

            self._event_dispatcher.dispatch(event=event)

            self._run_strategies(event=event)
        logger.info(self._portfolio.get_trading_metrics())
        logger.info(self._portfolio.get_trade_analysis())
        logger.info("engine stopped running")

    def _close_trades(self, event: MarketDataEvent):
        if closed_positions := self._positionManager.on_event(event=event):
            self._portfolio.add_trades(
                trades=closed_positions,
                current_price=event.payload.price,
                exit_timestamp=event.timestamp,
            )

    def _fill_submitted_orders(self, event: Event) -> None:
        if orders := self._orderManager.on_event(event=event):
            self._positionManager.on_fill_sequence(fills=orders)

    def _run_strategies(self, event: Event) -> None:
        for signal in self._strategy_handler.run_all_strategy(event=event):
            self._orderManager.handle_signal(
                signal=signal, time=self._clock.now
            )
