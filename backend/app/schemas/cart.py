from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    food_item_id: UUID
    quantity: int = Field(gt=0, le=50)
    customization: dict[str, Any] = Field(default_factory=dict)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0, le=50)
    customization: dict[str, Any] | None = None


class CartItemResponse(BaseModel):
    id: UUID
    food_item_id: UUID
    name: str
    quantity: int
    unit_price_minor: int
    customization: dict[str, Any]


class CartResponse(BaseModel):
    id: UUID
    restaurant_id: UUID | None
    items: list[CartItemResponse]
    subtotal_minor: int
