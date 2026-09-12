from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RestaurantSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    cuisine_types: list
    image_url: str | None
    status: str
    rating: Decimal


class FoodItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    restaurant_id: UUID
    category_id: UUID
    name: str
    description: str | None
    price_minor: int
    discount_percent: Decimal
    is_vegetarian: bool
    spice_level: int
    image_url: str | None
    is_available: bool
