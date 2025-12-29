# Custom
import event

from .clock import Clock
from common.enums import EventEnum
from .event_queue import EventQueue


class Engine:
    def __init__(self) -> None:
        self._queue = EventQueue()
        self._clock = Clock()
        self._running = False

    def push_event(self, event: event.Event) -> None:
        self._queue.push(event=event)

    def run(self) -> None:
        self._running = True
        while self._running and len(self._queue) > 0:
            event = self._queue.pop()
            self._clock.advance_to(timestamp=event.timestamp)
            self._dispatch(event=event)

    def stop(self) -> None:
        self._running = False

    def _dispatch(self, event: event.Event) -> None:
        event_type = event.event_type
        if event_type == EventEnum.MARKET_DATA:
            self._handle_market_data(event=event)
        elif event_type == EventEnum.ORDER_CANCEL:
            self._handle_order_cancel(event=event)
        elif event_type == EventEnum.ORDER_FILL:
            self._handle_order_fill(event=event)
        elif event_type == EventEnum.ORDER_SUBMIT:
            self._handle_order_submit(event=event)
        elif event_type == EventEnum.TIMER:
            self._handle_timer(event=event)
        else:
            raise NotImplementedError(event_type)

    def _handle_order_cancel(self, event: event.Event) -> None:
        pass

    def _handle_market_data(self, event: event.Event) -> None:
        pass

    def _handle_order_submit(self, event: event.Event) -> None:
        pass

    def _handle_order_fill(self, event: event.Event) -> None:
        pass

    def _handle_timer(self, event: event.Event) -> None:
        pass
