import pytest

from app.models.entities import OrderStatus
from app.orders.state_machine import InvalidOrderTransition, can_transition, transition


def test_happy_path_transitions_are_allowed() -> None:
    current = OrderStatus.CREATED
    for requested in (
        OrderStatus.PAYMENT_PENDING,
        OrderStatus.CONFIRMED,
        OrderStatus.RESTAURANT_ACCEPTED,
        OrderStatus.PREPARING,
        OrderStatus.READY_FOR_PICKUP,
        OrderStatus.PARTNER_ASSIGNED,
        OrderStatus.PICKED_UP,
        OrderStatus.OUT_FOR_DELIVERY,
        OrderStatus.DELIVERED,
    ):
        event = transition(current, requested)
        assert event.from_status == current
        assert event.to_status == requested
        current = requested


def test_delivered_cannot_return_to_preparing() -> None:
    assert not can_transition(OrderStatus.DELIVERED, OrderStatus.PREPARING)
    with pytest.raises(InvalidOrderTransition):
        transition(OrderStatus.DELIVERED, OrderStatus.PREPARING)


def test_transition_event_keeps_audit_note() -> None:
    event = transition(OrderStatus.PREPARING, OrderStatus.READY_FOR_PICKUP, "Kitchen packed order")
    assert event.note == "Kitchen packed order"
