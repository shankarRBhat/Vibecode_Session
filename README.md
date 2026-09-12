# FOODFLOW

**Discover. Order. Track. Enjoy.**

FOODFLOW is a modular food-delivery ecosystem for customers, restaurant owners, delivery partners, and administrators.

## Phase 1 status

This repository currently contains the architecture and database foundation: FastAPI health endpoint, SQLAlchemy domain schema, Alembic scaffolding, PostgreSQL/Redis Docker services, environment template, and Playwright agent setup.

## Start infrastructure

```powershell
docker compose up -d postgres redis
```

Copy `.env.example` to `.env`, then install the Python package:

```powershell
py -3.13 -m pip install -e ".[test]"
```

Python 3.13 is recommended because the backend dependencies publish compatible
Windows wheels for that version. Python 3.15 may require a local Rust/MSVC build
for Pydantic and is not the supported local runtime yet.

Apply migrations after generating the initial revision:

```powershell
alembic revision --autogenerate -m "create initial schema"
alembic upgrade head
```

Run the API:

```powershell
$env:PYTHONPATH = "backend"
uvicorn app.main:app --reload
```

Authentication endpoints are under `/api/v1/auth`: register, login, refresh,
and the protected `/me` endpoint. Public registration cannot create an admin
account; admin users must be provisioned by an operator.

Delivery assignment uses a weighted strategy across distance, availability,
workload, rating, and acceptance rate. ETA currently uses a documented rule-based
strategy with preparation time, route distance, traffic simulation, active-order
load, and historical delivery time.

Health check: `GET http://localhost:8000/health`

## Product roadmap

Authentication and role authorization come next, followed by customer discovery, cart and checkout, restaurant operations, delivery assignment, realtime tracking, analytics, recommendations, and full testing.

Development-only payment, maps, GPS, and AI services will remain explicitly abstracted and labeled until real providers are configured.
