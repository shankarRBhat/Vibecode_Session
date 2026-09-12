# FOODFLOW Database

PostgreSQL is the source of truth. UUID keys identify domain records. Monetary values use integer minor units such as paise, and timestamps use timezone-aware values.

## Domains

- Identity: `users`, `user_roles`, `addresses`
- Restaurant: `restaurants`, `restaurant_documents`, `food_categories`, `food_items`, `food_addons`
- Commerce: `carts`, `cart_items`, `coupons`, `coupon_usage`, `orders`, `order_items`
- Payment: `payments`, `refunds`
- Delivery: `delivery_partners`, `delivery_assignments`, `delivery_locations`
- Trust and engagement: `reviews`, `favorites`, `notifications`
- Intelligence: `user_search_history`, `user_view_history`, `recommendations`
- Audit: `order_status_history`

The SQLAlchemy metadata defines foreign keys, indexes, unique constraints, and checks for positive quantities, valid spice levels, non-negative prices, and ratings from one to five. Generate and apply migrations with Alembic after starting PostgreSQL.
