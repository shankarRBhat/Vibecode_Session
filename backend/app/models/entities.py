import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserRole(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    RESTAURANT_OWNER = "RESTAURANT_OWNER"
    DELIVERY_PARTNER = "DELIVERY_PARTNER"
    ADMIN = "ADMIN"


class RestaurantStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REJECTED = "REJECTED"


class OrderStatus(str, enum.Enum):
    CREATED = "CREATED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    CONFIRMED = "CONFIRMED"
    RESTAURANT_ACCEPTED = "RESTAURANT_ACCEPTED"
    PREPARING = "PREPARING"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    PARTNER_ASSIGNED = "PARTNER_ASSIGNED"
    PICKED_UP = "PICKED_UP"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    REFUND_REQUESTED = "REFUND_REQUESTED"
    REFUNDED = "REFUNDED"


class PaymentStatus(str, enum.Enum):
    INITIATED = "INITIATED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUND_PENDING = "REFUND_PENDING"
    REFUNDED = "REFUNDED"


class TimestampEntity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __abstract__ = True


class User(TimestampEntity):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(160))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class UserRoleAssignment(TimestampEntity):
    __tablename__ = "user_roles"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(32), index=True)
    __table_args__ = (UniqueConstraint("user_id", "role", name="uq_user_role"),)


class Address(TimestampEntity):
    __tablename__ = "addresses"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(64))
    line1: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(120))
    postal_code: Mapped[str] = mapped_column(String(20))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)


class Restaurant(TimestampEntity):
    __tablename__ = "restaurants"
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(180), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    cuisine_types: Mapped[list] = mapped_column(JSONB, default=list)
    image_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(32), default=RestaurantStatus.PENDING.value, index=True)
    rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=0)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))


class RestaurantDocument(TimestampEntity):
    __tablename__ = "restaurant_documents"
    restaurant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("restaurants.id", ondelete="CASCADE"), index=True)
    document_type: Mapped[str] = mapped_column(String(64))
    document_url: Mapped[str] = mapped_column(String(500))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)


class FoodCategory(TimestampEntity):
    __tablename__ = "food_categories"
    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)


class FoodItem(TimestampEntity):
    __tablename__ = "food_items"
    restaurant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("restaurants.id", ondelete="CASCADE"), index=True)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("food_categories.id"), index=True)
    name: Mapped[str] = mapped_column(String(180), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    price_minor: Mapped[int] = mapped_column(Integer)
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    is_vegetarian: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    spice_level: Mapped[int] = mapped_column(Integer, default=0)
    image_url: Mapped[str | None] = mapped_column(String(500))
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    __table_args__ = (CheckConstraint("price_minor >= 0", name="ck_food_price_nonnegative"), CheckConstraint("spice_level between 0 and 5", name="ck_spice_level"))


class FoodAddon(TimestampEntity):
    __tablename__ = "food_addons"
    food_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("food_items.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    price_minor: Mapped[int] = mapped_column(Integer, default=0)


class Cart(TimestampEntity):
    __tablename__ = "carts"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    restaurant_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("restaurants.id"))


class CartItem(TimestampEntity):
    __tablename__ = "cart_items"
    cart_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("carts.id", ondelete="CASCADE"), index=True)
    food_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("food_items.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    customization: Mapped[dict] = mapped_column(JSONB, default=dict)
    __table_args__ = (CheckConstraint("quantity > 0", name="ck_cart_quantity_positive"),)


class Coupon(TimestampEntity):
    __tablename__ = "coupons"
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    discount_type: Mapped[str] = mapped_column(String(16))
    discount_value: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    minimum_order_minor: Mapped[int] = mapped_column(Integer, default=0)
    maximum_discount_minor: Mapped[int | None] = mapped_column(Integer)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    usage_limit: Mapped[int | None] = mapped_column(Integer)
    per_user_limit: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Order(TimestampEntity):
    __tablename__ = "orders"
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("restaurants.id"), index=True)
    delivery_address_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("addresses.id"))
    coupon_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("coupons.id"))
    status: Mapped[str] = mapped_column(String(32), default=OrderStatus.CREATED.value, index=True)
    subtotal_minor: Mapped[int] = mapped_column(Integer)
    delivery_fee_minor: Mapped[int] = mapped_column(Integer)
    tax_minor: Mapped[int] = mapped_column(Integer)
    discount_minor: Mapped[int] = mapped_column(Integer, default=0)
    total_minor: Mapped[int] = mapped_column(Integer)
    eta_minutes: Mapped[int | None] = mapped_column(Integer)
    __table_args__ = (Index("ix_orders_restaurant_status", "restaurant_id", "status"), CheckConstraint("total_minor >= 0", name="ck_order_total_nonnegative"))


class OrderItem(TimestampEntity):
    __tablename__ = "order_items"
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    food_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("food_items.id"))
    item_name: Mapped[str] = mapped_column(String(180))
    unit_price_minor: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)
    customization: Mapped[dict] = mapped_column(JSONB, default=dict)


class OrderStatusHistory(TimestampEntity):
    __tablename__ = "order_status_history"
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    from_status: Mapped[str | None] = mapped_column(String(32))
    to_status: Mapped[str] = mapped_column(String(32))
    changed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    note: Mapped[str | None] = mapped_column(Text)


class Payment(TimestampEntity):
    __tablename__ = "payments"
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), unique=True)
    method: Mapped[str] = mapped_column(String(24))
    status: Mapped[str] = mapped_column(String(24), default=PaymentStatus.INITIATED.value, index=True)
    gateway_reference: Mapped[str | None] = mapped_column(String(180), unique=True)
    amount_minor: Mapped[int] = mapped_column(Integer)


class Refund(TimestampEntity):
    __tablename__ = "refunds"
    payment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("payments.id"), index=True)
    amount_minor: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(24), default=PaymentStatus.REFUND_PENDING.value)
    reason: Mapped[str | None] = mapped_column(Text)


class DeliveryPartner(TimestampEntity):
    __tablename__ = "delivery_partners"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    vehicle_type: Mapped[str] = mapped_column(String(32))
    vehicle_number: Mapped[str | None] = mapped_column(String(32), unique=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=0)
    active_order_count: Mapped[int] = mapped_column(Integer, default=0)


class DeliveryAssignment(TimestampEntity):
    __tablename__ = "delivery_assignments"
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), unique=True)
    partner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("delivery_partners.id"), index=True)
    matching_score: Mapped[Decimal] = mapped_column(Numeric(8, 4))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class DeliveryLocation(TimestampEntity):
    __tablename__ = "delivery_locations"
    assignment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("delivery_assignments.id", ondelete="CASCADE"), index=True)
    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class CouponUsage(TimestampEntity):
    __tablename__ = "coupon_usage"
    coupon_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("coupons.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), unique=True)


class Review(TimestampEntity):
    __tablename__ = "reviews"
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("orders.id"), index=True)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("restaurants.id"), index=True)
    food_item_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("food_items.id"))
    delivery_rating: Mapped[int | None] = mapped_column(Integer)
    food_rating: Mapped[int | None] = mapped_column(Integer)
    restaurant_rating: Mapped[int | None] = mapped_column(Integer)
    body: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (CheckConstraint("restaurant_rating between 1 and 5", name="ck_restaurant_rating"),)


class Favorite(TimestampEntity):
    __tablename__ = "favorites"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("restaurants.id", ondelete="CASCADE"), index=True)
    __table_args__ = (UniqueConstraint("user_id", "restaurant_id", name="uq_favorite_restaurant"),)


class Notification(TimestampEntity):
    __tablename__ = "notifications"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(180))
    body: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class UserSearchHistory(TimestampEntity):
    __tablename__ = "user_search_history"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    query: Mapped[str] = mapped_column(String(255), index=True)
    filters: Mapped[dict] = mapped_column(JSONB, default=dict)


class UserViewHistory(TimestampEntity):
    __tablename__ = "user_view_history"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    restaurant_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("restaurants.id"))
    food_item_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("food_items.id"))


class Recommendation(TimestampEntity):
    __tablename__ = "recommendations"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    restaurant_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("restaurants.id"))
    food_item_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("food_items.id"))
    reason: Mapped[str] = mapped_column(String(255))
    score: Mapped[Decimal] = mapped_column(Numeric(8, 4))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
