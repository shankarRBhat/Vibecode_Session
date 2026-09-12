from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.session import get_db
from app.models.entities import Cart, CartItem, FoodItem, User
from app.schemas.cart import CartItemCreate, CartItemResponse, CartItemUpdate, CartResponse

router = APIRouter(prefix="/api/v1/cart", tags=["cart"])


def _cart_response(db: Session, cart: Cart) -> CartResponse:
    rows = db.execute(select(CartItem, FoodItem).join(FoodItem, FoodItem.id == CartItem.food_item_id).where(CartItem.cart_id == cart.id)).all()
    items = [CartItemResponse(id=item.id, food_item_id=item.food_item_id, name=food.name, quantity=item.quantity, unit_price_minor=food.price_minor, customization=item.customization) for item, food in rows]
    return CartResponse(id=cart.id, restaurant_id=cart.restaurant_id, items=items, subtotal_minor=sum(item.unit_price_minor * item.quantity for item in items))


def _get_or_create_cart(db: Session, user_id: UUID) -> Cart:
    cart = db.scalar(select(Cart).where(Cart.user_id == user_id))
    if cart is None:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.flush()
    return cart


@router.get("", response_model=CartResponse)
def get_cart(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CartResponse:
    return _cart_response(db, _get_or_create_cart(db, user.id))


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_cart_item(payload: CartItemCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CartResponse:
    cart = _get_or_create_cart(db, user.id)
    food = db.get(FoodItem, payload.food_item_id)
    if food is None or not food.is_available:
        raise HTTPException(status_code=404, detail={"code": "FOOD_NOT_AVAILABLE", "message": "Food item is not available"})
    if cart.restaurant_id and cart.restaurant_id != food.restaurant_id:
        raise HTTPException(status_code=409, detail={"code": "CART_RESTAURANT_MISMATCH", "message": "Cart can contain items from one restaurant"})
    cart.restaurant_id = food.restaurant_id
    item = db.scalar(select(CartItem).where(CartItem.cart_id == cart.id, CartItem.food_item_id == food.id))
    if item is None:
        db.add(CartItem(cart_id=cart.id, food_item_id=food.id, quantity=payload.quantity, customization=payload.customization))
    else:
        item.quantity += payload.quantity
        item.customization = payload.customization
    db.commit()
    return _cart_response(db, cart)


@router.put("/items/{item_id}", response_model=CartResponse)
def update_cart_item(item_id: UUID, payload: CartItemUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CartResponse:
    cart = _get_or_create_cart(db, user.id)
    item = db.scalar(select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id))
    if item is None:
        raise HTTPException(status_code=404, detail={"code": "CART_ITEM_NOT_FOUND", "message": "Cart item does not exist"})
    item.quantity = payload.quantity
    if payload.customization is not None:
        item.customization = payload.customization
    db.commit()
    return _cart_response(db, cart)


@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_cart_item(item_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CartResponse:
    cart = _get_or_create_cart(db, user.id)
    item = db.scalar(select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id))
    if item is None:
        raise HTTPException(status_code=404, detail={"code": "CART_ITEM_NOT_FOUND", "message": "Cart item does not exist"})
    db.delete(item)
    db.flush()
    if db.scalar(select(CartItem.id).where(CartItem.cart_id == cart.id)) is None:
        cart.restaurant_id = None
    db.commit()
    return _cart_response(db, cart)
