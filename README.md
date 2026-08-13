# Whitfield Fulfillment WMS — Backend API

FastAPI + MongoDB (single-node replica set `rs0`) REST API backend.

## Architecture

```
WMS/
  main.py                      ← FastAPI app entry; uvicorn main:app --reload
  core/
    apis/
      api.py                   ← Root FastAPI app, lifespan, middleware, router wiring
      routes/                  ← *_router.py per domain
        health_router.py
        auth_router.py
        user_router.py
        facility_router.py     ← warehouse endpoints at /warehouses
        audit_router.py
        inbox_router.py
        arrival_router.py
        ticket_router.py
        approval_router.py     ← GET /approvals, POST /tickets/{id}/approve
        storage_router.py
        order_router.py
        report_router.py
        voice_router.py
        vision_router.py
        query_router.py
        api_key_router.py
      schemas/
        requests/              ← *_request.py Pydantic request models
        responses/             ← *_response.py Pydantic response models
    config/
      settings.py              ← pydantic-settings; loads .env
    controllers/               ← ALL business logic + transactions
    cruds/
      base.py                  ← BaseCRUD helpers
      facility_crud.py         ← Warehouse facility Mongo access
      *_crud.py                ← One per domain
    database/
      database.py              ← Motor client, get_db, ping, close
      init_db.py               ← Collections + indexes bootstrap
    models/                    ← DB document models
      facility_model.py        ← Warehouse document schema
    services/                  ← External integrations (STT, LLM, vision)
    utils/
      ticket_generator.py      ← Atomic counter-based ticket ID generation
  commons/
    auth.py                    ← JWT decode + RBAC require_roles dependency
    logger.py                  ← Structured logging setup
    exceptions.py              ← WMSException base + HTTP exception factories
  tests/
    conftest.py                ← Shared fixtures
    phase01/                   ← Auth, RBAC, ticket generator tests
    phase02plus/               ← Inbound flow, orders, concurrency, reports, AI
    smoke/                     ← Health + core workflow smoke tests
  scripts/
    migrate_excel.py
    seed_owner.py
  logs/                        ← Runtime log files (git-ignored)
```

## Running

```bash
# Start the API (from WMS/ root)
uvicorn main:app --reload --port 8000

# Or
python main.py
```

## Database Initialization

```bash
# Initialize MongoDB collections + indexes (idempotent)
python -m core.database.init_db
```

## Testing

```bash
# Run all tests
python -m pytest -q

# Run by phase
python -m pytest tests/phase01/ -q
python -m pytest tests/phase02plus/ -q
python -m pytest tests/smoke/ -q
```

## Linting

```bash
ruff check .
ruff check . --fix
```

## Environment

Copy `.env.example` to `.env` and set values. MongoDB must run as a replica set:

```bash
# One-shot rs0 setup (PowerShell)
.\setup_rs0.ps1
```

## Branch

Active development: `restructure-layout` (refactored from initial commit — zero behavior change, 34 tests pass).

## Codex Skills

Use `.codex/skills/eigi-backend-standards` for backend API work.
