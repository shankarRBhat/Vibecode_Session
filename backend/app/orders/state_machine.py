from dataclasses import dataclass

from app.models.entities import OrderStatus


class InvalidOrderTransition(ValueError):
    def __init__(self, current: OrderStatus, requested: OrderStatus) -> None:
        super().__init__(f"Cannot transition order from {current.value} to {requested.value}")
        self.current = current
        self.requested = requested


_ALLOWED_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
    OrderStatus.CREATED: frozenset({OrderStatus.PAYMENT_PENDING, OrderStatus.CANCELLED}),
    OrderStatus.PAYMENT_PENDING: frozenset({OrderStatus.CONFIRMED, OrderStatus.CANCELLED}),
    OrderStatus.CONFIRMED: frozenset({OrderStatus.RESTAURANT_ACCEPTED, OrderStatus.CANCELLED}),
    OrderStatus.RESTAURANT_ACCEPTED: frozenset({OrderStatus.PREPARING, OrderStatus.CANCELLED}),
    OrderStatus.PREPARING: frozenset({OrderStatus.READY_FOR_PICKUP, OrderStatus.CANCELLED}),
    OrderStatus.READY_FOR_PICKUP: frozenset({OrderStatus.PARTNER_ASSIGNED, OrderStatus.CANCELLED}),
    OrderStatus.PARTNER_ASSIGNED: frozenset({OrderStatus.PICKED_UP, OrderStatus.CANCELLED}),
    OrderStatus.PICKED_UP: frozenset({OrderStatus.OUT_FOR_DELIVERY}),
    OrderStatus.OUT_FOR_DELIVERY: frozenset({OrderStatus.DELIVERED}),
    OrderStatus.DELIVERED: frozenset({OrderStatus.REFUND_REQUESTED}),
    OrderStatus.REFUND_REQUESTED: frozenset({OrderStatus.REFUNDED}),
    OrderStatus.CANCELLED: frozenset(),
    OrderStatus.REFUNDED: frozenset(),
}


@dataclass(frozen=True)
class OrderTransition:
    from_status: OrderStatus
    to_status: OrderStatus
    note: str | None = None


def can_transition(current: OrderStatus, requested: OrderStatus) -> bool:
    return requested in _ALLOWED_TRANSITIONS[current]


def transition(current: OrderStatus, requested: OrderStatus, note: str | None = None) -> OrderTransition:
    if not can_transition(current, requested):
        raise InvalidOrderTransition(current, requested)
    return OrderTransition(from_status=current, to_status=requested, note=note)
