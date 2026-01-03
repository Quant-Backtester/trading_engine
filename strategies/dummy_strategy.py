from .strategy import Strategy
from events.event import Event

class DummyStrategy(Strategy):
    def __init__(self):
        self.events: list[Event] = []

    def on_event(self, event: Event) -> None:
        self.events.append(event)
