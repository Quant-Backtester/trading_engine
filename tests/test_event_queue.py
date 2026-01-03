# STL
import unittest

from events.enums import EventEnum
from events.payloads import TestingPayload
from events.event import Event

# Custom
from core.event_queue import EventQueue


class TestEventQueue(unittest.TestCase):
    def setUp(self) -> None:
        self.queue = EventQueue()
        payload = TestingPayload(order_id=1)
        self.test_event = Event(
            timestamp=1, event_type=EventEnum.TIMER, payload=payload
        )

    def test_pop_empty_queue(self) -> None:
        with self.assertRaises(IndexError):
            self.queue.pop()

    def test_single_event(self) -> None:
        payload = TestingPayload(order_id=1)
        e = Event(10, EventEnum.TIMER, payload=payload)
        self.queue.push(e)
        self.assertEqual(len(self.queue), 1)
        out = self.queue.pop()
        self.assertEqual(out, e)
        self.assertEqual(len(self.queue), 0)

    def test_check_empty(self) -> None:
        self.assertTrue(self.queue.check_empty())
        self.queue.push(self.test_event)
        self.assertFalse(self.queue.check_empty())

    def test_peek(self) -> None:
        with self.assertRaises(IndexError):
            self.queue.peek()

        self.queue.push(self.test_event)
        self.assertEqual(self.test_event, self.queue.peek())

    def test_sequence_number(self) -> None:
        self.queue.push(self.test_event)
        self.assertEqual(self.queue.sequence_number, 1)

        self.queue.peek()
        self.assertEqual(self.queue.sequence_number, 1)

        self.queue.pop()
        self.assertEqual(self.queue.sequence_number, 1)

    def test_determinism(self) -> None:
        def run_once():
            payload1 = TestingPayload(order_id=1)
            payload2 = TestingPayload(order_id=2)
            test_event1 = Event(
                timestamp=1, event_type=EventEnum.ORDER_CANCEL, payload=payload1
            )
            test_event2 = Event(
                timestamp=2, event_type=EventEnum.ORDER_CANCEL, payload=payload2
            )
            self.queue.push(event=test_event1)
            self.queue.push(event=test_event2)
            return [self.queue.pop(), self.queue.pop()]

        self.assertEqual(run_once(), run_once())
