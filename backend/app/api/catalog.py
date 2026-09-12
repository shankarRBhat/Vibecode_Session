from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.entities import FoodItem, Restaurant, RestaurantStatus
from app.schemas.catalog import FoodItemResponse, RestaurantSummary

router = APIRouter(prefix="/api/v1/restaurants", tags=["restaurants"])


@router.get("", response_model=list[RestaurantSummary])
def list_restaurants(
    query: str | None = Query(default=None, min_length=1, max_length=120),
    vegetarian: bool | None = None,
    db: Session = Depends(get_db),
) -> list[Restaurant]:
    statement: Select[tuple[Restaurant]] = select(Restaurant).where(Restaurant.status == RestaurantStatus.ACTIVE.value)
    if query:
        statement = statement.where(Restaurant.name.ilike(f"%{query}%"))
    if vegetarian:
        statement = statement.where(Restaurant.cuisine_types.contains(["VEG"]))
    return list(db.scalars(statement.order_by(Restaurant.rating.desc())).all())


@router.get("/{restaurant_id}", response_model=RestaurantSummary)
def get_restaurant(restaurant_id: UUID, db: Session = Depends(get_db)) -> Restaurant:
    restaurant = db.scalar(select(Restaurant).where(Restaurant.id == restaurant_id, Restaurant.status == RestaurantStatus.ACTIVE.value))
    if restaurant is None:
        raise HTTPException(status_code=404, detail={"code": "RESTAURANT_NOT_FOUND", "message": "Restaurant does not exist"})
    return restaurant


@router.get("/{restaurant_id}/menu", response_model=list[FoodItemResponse])
def get_menu(restaurant_id: UUID, db: Session = Depends(get_db)) -> list[FoodItem]:
    if db.scalar(select(Restaurant.id).where(Restaurant.id == restaurant_id, Restaurant.status == RestaurantStatus.ACTIVE.value)) is None:
        raise HTTPException(status_code=404, detail={"code": "RESTAURANT_NOT_FOUND", "message": "Restaurant does not exist"})
    return list(db.scalars(select(FoodItem).where(FoodItem.restaurant_id == restaurant_id, FoodItem.is_available.is_(True)).order_by(FoodItem.name)).all())
