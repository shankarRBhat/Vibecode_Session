from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    delivery_address_id: UUID
    payment_method: str = Field(pattern="^(CARD|UPI|WALLET|COD)$")


class OrderItemResponse(BaseModel):
    food_item_id: UUID
    item_name: str
    unit_price_minor: int
    quantity: int
    customization: dict


class OrderResponse(BaseModel):
    id: UUID
    restaurant_id: UUID
    status: str
    subtotal_minor: int
    delivery_fee_minor: int
    tax_minor: int
    discount_minor: int
    total_minor: int
    created_at: datetime
    items: list[OrderItemResponse]
