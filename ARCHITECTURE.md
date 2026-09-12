# FOODFLOW Architecture

FOODFLOW starts as a modular monolith with explicit service boundaries. The boundary is deliberately inside one deployable FastAPI application so local development stays simple while future extraction into services remains possible.

## Runtime topology

- React + TypeScript frontend
- FastAPI REST and WebSocket API
- PostgreSQL as the source of truth
- Redis for cache, rate limiting, sessions, and job coordination
- Background job abstraction for notifications, analytics, and timeouts
- Adapters for payments, maps, email, push, and AI

## Backend boundaries

`auth`, `users`, `restaurants`, `menu`, `search`, `cart`, `orders`, `payments`, `delivery`, `notifications`, `recommendations`, `analytics`, and `admin` each own their routes, schemas, services, and repositories. Routes validate and authorize; services own business rules; repositories own persistence.

## Integration rules

External providers are accessed through interfaces. Development uses mock payment, simulated GPS, rule-based ETA, PostgreSQL search, and content-based recommendations. None are presented as production integrations.

## Security baseline

Secrets come from environment variables. Passwords are hashed, access is role-checked server-side, API errors are structured, and payment credentials are never stored. Database access uses SQLAlchemy parameters and constraints.
