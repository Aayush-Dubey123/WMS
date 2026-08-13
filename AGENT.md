# Eigi Skills

This repo stores reusable Codex skills under `.codex/skills/`.
Use `.codex/skills/eigi-backend-standards` for Eigi backend API work.
It guides route, controller, CRUD, service, schema, model, logging, docstring, test, and backend `.gitignore` standards.
Use `.codex/skills/eigi-frontend-standards` for Eigi frontend web app work.
It guides route/page, feature component, shared UI, API client, hook/store, styling, test, env, and frontend `.gitignore` standards.
Inspect nearby code first and follow the closest local convention.
Keep detailed standards inside each skill's `SKILL.md` and load references only when needed.

## WMS Repo Layout (post-restructure)

```
WMS/
  main.py                         ← `uvicorn main:app --reload` from WMS/ root
  core/
    apis/
      api.py                      ← FastAPI app + all router wiring
      routes/                     ← *_router.py (facility_, approval_, etc.)
      schemas/requests/           ← *_request.py
      schemas/responses/          ← *_response.py
    config/settings.py
    controllers/                  ← Business logic (*_controller.py)
    cruds/base.py + *_crud.py     ← facility_crud.py owns warehouse docs
    database/database.py + init_db.py
    models/                       ← *_model.py (facility_model.py for warehouses)
    services/                     ← External integrations
    utils/ticket_generator.py
  commons/
    auth.py                       ← JWT + RBAC
    logger.py
    exceptions.py                 ← WMSException + HTTP helpers
  tests/
    conftest.py
    phase01/                      ← Auth, RBAC, ticket generator
    phase02plus/                  ← Inbound, orders, reports, AI, API keys
    smoke/                        ← Health + workflow smoke tests
  scripts/                        ← One-off scripts (migrate_excel, seed_owner)
  logs/                           ← Runtime logs (git-ignored)
```

## Key Commands

```bash
uvicorn main:app --reload         # serve from WMS/ root
python -m core.database.init_db   # bootstrap collections + indexes
python -m pytest -q               # run all tests (baseline: 34 passed)
ruff check .                      # lint
```
