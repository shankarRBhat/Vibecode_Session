from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.session import get_db
from app.models.entities import Address, Cart, CartItem, FoodItem, Order, OrderItem, OrderStatus, Payment, User
from app.orders.state_machine import InvalidOrderTransition, transition
from app.schemas.orders import OrderCreate, OrderItemResponse, OrderResponse

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


def _order_response(order: Order, items: list[OrderItem]) -> OrderResponse:
    return OrderResponse(id=order.id, restaurant_id=order.restaurant_id, status=order.status, subtotal_minor=order.subtotal_minor, delivery_fee_minor=order.delivery_fee_minor, tax_minor=order.tax_minor, discount_minor=order.discount_minor, total_minor=order.total_minor, created_at=order.created_at, items=[OrderItemResponse(food_item_id=item.food_item_id, item_name=item.item_name, unit_price_minor=item.unit_price_minor, quantity=item.quantity, customization=item.customization) for item in items])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> OrderResponse:
    address = db.scalar(select(Address).where(Address.id == payload.delivery_address_id, Address.user_id == user.id))
    cart = db.scalar(select(Cart).where(Cart.user_id == user.id))
    if address is None:
        raise HTTPException(status_code=404, detail={"code": "ADDRESS_NOT_FOUND", "message": "Delivery address does not belong to this user"})
    if cart is None or cart.restaurant_id is None:
        raise HTTPException(status_code=400, detail={"code": "CART_EMPTY", "message": "Add items before checking out"})
    rows = db.execute(select(CartItem, FoodItem).join(FoodItem, FoodItem.id == CartItem.food_item_id).where(CartItem.cart_id == cart.id)).all()
    if not rows:
        raise HTTPException(status_code=400, detail={"code": "CART_EMPTY", "message": "Add items before checking out"})
    subtotal = sum(food.price_minor * item.quantity for item, food in rows)
    delivery_fee = 0 if subtotal >= 50000 else 4000
    tax = round(subtotal * 0.05)
    order = Order(customer_id=user.id, restaurant_id=cart.restaurant_id, delivery_address_id=address.id, status=OrderStatus.PAYMENT_PENDING.value, subtotal_minor=subtotal, delivery_fee_minor=delivery_fee, tax_minor=tax, discount_minor=0, total_minor=subtotal + delivery_fee + tax)
    db.add(order)
    db.flush()
    order_items = [OrderItem(order_id=order.id, food_item_id=food.id, item_name=food.name, unit_price_minor=food.price_minor, quantity=item.quantity, customization=item.customization) for item, food in rows]
    db.add_all(order_items)
    db.add(Payment(order_id=order.id, method=payload.payment_method, status="INITIATED", amount_minor=order.total_minor))
    for item, _ in rows:
        db.delete(item)
    cart.restaurant_id = None
    db.commit()
    db.refresh(order)
    return _order_response(order, order_items)


@router.get("", response_model=list[OrderResponse])
def list_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[OrderResponse]:
    orders = list(db.scalars(select(Order).where(Order.customer_id == user.id).order_by(Order.created_at.desc())).all())
    return [_order_response(order, list(db.scalars(select(OrderItem).where(OrderItem.order_id == order.id)).all())) for order in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> OrderResponse:
    order = db.scalar(select(Order).where(Order.id == order_id, Order.customer_id == user.id))
    if order is None:
        raise HTTPException(status_code=404, detail={"code": "ORDER_NOT_FOUND", "message": "Order does not exist"})
    return _order_response(order, list(db.scalars(select(OrderItem).where(OrderItem.order_id == order.id)).all()))


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> OrderResponse:
    order = db.scalar(select(Order).where(Order.id == order_id, Order.customer_id == user.id))
    if order is None:
        raise HTTPException(status_code=404, detail={"code": "ORDER_NOT_FOUND", "message": "Order does not exist"})
    try:
        transition(OrderStatus(order.status), OrderStatus.CANCELLED, "Cancelled by customer")
    except (InvalidOrderTransition, ValueError) as error:
        raise HTTPException(status_code=409, detail={"code": "INVALID_ORDER_TRANSITION", "message": str(error)}) from error
    order.status = OrderStatus.CANCELLED.value
    db.commit()
    db.refresh(order)
    return _order_response(order, list(db.scalars(select(OrderItem).where(OrderItem.order_id == order.id)).all()))
