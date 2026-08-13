# Whitfield Fulfillment WMS — Backend Implementation Plan
### Scope: BACKEND ONLY · FastAPI (Python 3.11+) · MongoDB (replica set) · JWT Auth

> ## ⚠️ Development Rule — READ FIRST (for all agents and skills)
> This project MUST be built **strictly phase by phase, in order**. Do not start a later phase before the current phase is complete, tested, and reviewed. Do not scaffold frontend code — the frontend is a separate later project; this repo exposes a REST API only. Each phase ends with its endpoints working, its tests passing, and its OpenAPI docs updated. If a task seems to belong to a later phase, defer it and note it in `BACKLOG.md`.

---

## System Summary (context for every phase)

Two-warehouse fulfillment system replacing Excel. Core spine: a **Ticket ID** (`{WH}-{YYYYMMDD}-{SEQ}`, e.g. `RNO-20260813-014`) follows every item from arrival → inspection → manager approval → storage → retrieval → sold. Role chain: **Owner** (creates warehouses + managers, deletes managers only) → **Manager** (creates staff, assigns Rookie/Experienced + function roles, approves shipments) → **Staff** (scan, log, inspect, pack). Rookie entries stay `PENDING_INSPECTION` until a Manager marks `SHIPMENT_ARRIVED`. All stock movement happens inside MongoDB transactions — no duplication, no oversell, everything audited.

**Item/Ticket status enum (fixed, do not extend without approval):**
`ANNOUNCED → ACCEPTED → ARRIVED → PENDING_INSPECTION → INSPECTED → SHIPMENT_ARRIVED → STORED → RESERVED → SOLD`
(side states: `DECLINED`, `NEEDS_SPEC`, `DAMAGED`, `NO_TICKET_ARRIVAL` flag)

---

## Phase 0 — Project Foundations

**Goal:** Runnable skeleton with DB, config, and conventions locked.

- Project layout (routers → services → repositories; all business logic in services):
```
app/
  main.py
  core/          # config, security, db client, exceptions
  models/        # pydantic schemas (request/response/db)
  routers/       # thin HTTP layer only
  services/      # ALL business logic + transactions
  repositories/  # mongo queries only
  utils/         # ticket_generator, audit, idempotency
tests/
```
- MongoDB via `motor` (async), **replica set required** (single-node replica set is fine in dev: needed for multi-document transactions).
- Collections + indexes created by a startup/migration script:
  - `users`, `warehouses`, `inbox_shipments`, `tickets`, `items`, `orders`, `storage_locations`, `audit_log`, `counters` (for daily ticket sequence), `api_keys`
  - Unique indexes: `users.email`, `tickets.ticket_id`, `items.ticket_id + unit_seq`, idempotency keys.
- `.env` config via pydantic-settings; structured logging; global exception handlers; health endpoint `GET /health`.
- Ticket generator utility: atomic `findOneAndUpdate` on `counters` per warehouse+date → `{WH}-{YYYYMMDD}-{SEQ}`.
- Tooling: pytest + httpx async test client, ruff, pre-commit, Dockerfile + docker-compose (api + mongo replica set).

**Exit criteria:** `docker compose up` serves `/health` and `/docs`; index script idempotent; CI runs tests + lint.

---

## Phase 1 — Auth, Role Hierarchy, RBAC & Audit

**Goal:** Single login for all roles; Owner→Manager→Staff chain; every write audited.

- **Auth:** `POST /auth/login` (JWT access + refresh), `POST /auth/refresh`, `GET /auth/me`. Password hashing with argon2/bcrypt. JWT carries `role`, `warehouse_id` (null for Owner), `experience_tier`.
- **Roles:** `OWNER`, `MANAGER`, `STAFF` (+ `experience_tier: ROOKIE|EXPERIENCED`, `function_roles: [LISTING, PACKING, RECEIVING, ...]`).
- **Owner endpoints:** create warehouse; create manager; **delete (soft) manager only** — deleting a manager requires reassigning their staff. Owner cannot create staff (by design).
- **Manager endpoints:** create staff scoped to own warehouse; set tier + function roles; deactivate staff.
- **RBAC dependency:** FastAPI dependency `require(roles=…, functions=…)` on every route; warehouse scoping enforced server-side (a manager can never read/write another warehouse).
- **Audit:** service-layer hook writes `{actor_id, action, collection, doc_id, before, after, ts}` to `audit_log` on every mutation. `GET /audit` (Owner/Manager, filterable).
- Seed script: first Owner account.

**Exit criteria:** Full invitation chain works via API; permission matrix covered by tests (each role tested against each endpoint); audit rows written for all mutations.

---

## Phase 2 — Inbox, Arrival, Ticketing & Inspection

**Goal:** Inbound flow from "seller announces parcel" to "manager approves shipment," fully by API.

- **Inbox:** `POST /inbox` (announce incoming parcel: seller, expected items, carrier tracking optional) → status `ANNOUNCED`. Manager/Owner: `POST /inbox/{id}/accept | /decline | /revert` (revert = `NEEDS_SPEC` + comment thread on the doc).
- **Arrival:**
  - `POST /arrivals` — match by tracking number to an accepted inbox entry, **or** flag `no_ticket_arrival=true` → system generates ticket via counter (marking "arrived with no ticket" is mandatory data, not a note).
  - `POST /tickets/{ticket_id}/items` — barcode (UPC) scan payload binds product → ticket; per unit log: `width, height, weight, image_url (optional), damage {flag, note}, logged_by (auto), ts (auto)`. Idempotency-Key header required — resubmits (frozen laptop case) can never double-log.
  - Image upload endpoint → object storage (local volume in dev, S3-compatible interface).
- **Inspection & approval layer:** Rookie completes logging → `PUT /tickets/{id}/submit-inspection` → `PENDING_INSPECTION`. Manager queue: `GET /approvals`, `POST /tickets/{id}/approve` → `SHIPMENT_ARRIVED`. Only then are units sellable. Damaged units tracked as separate quantity, never sellable.
- **Storage:** `POST /tickets/{id}/store` assigns `storage_location` (zone/rack/bin string codes) → `STORED`.
- Duplicate guard: warn/reject on same tracking number or identical line-set submitted twice.

**Exit criteria:** End-to-end inbound test (announce → accept → arrive → scan → inspect → approve → store) green, including the duplicate-submission and no-ticket-arrival cases.

---

## Phase 3 — Orders, Retrieval & Anti-Duplication Selling

**Goal:** Oversell-proof outbound flow; sold items roll into totals.

- `POST /orders` (manual intake; channel connectors are out of scope — backlog).
- **Atomic reservation (the core controller logic):** `POST /orders/{id}/reserve` runs a MongoDB **transaction**: verify each unit `STORED` → set `RESERVED` + attach order ref. Concurrent requests for the same unit: one commits, one gets HTTP 409. Covered by a dedicated concurrency test (parallel requests).
- Pick/pack: `GET /orders/{id}/picklist` (returns storage locations by ticket ID), `POST /orders/{id}/pack` (confirm/override weight & dims), label stub endpoint (carrier API integration behind an interface; real EasyPost/Shippo key optional).
- `POST /orders/{id}/ship` → units `SOLD`, timestamps recorded; sold quantities immediately reflected in totals aggregations (Phase 4 consumes these).
- Cancel/return path: `RESERVED → STORED` release inside a transaction.

**Exit criteria:** Concurrency test proves double-sell impossible; full outbound lifecycle test green; every transition audited.

---

## Phase 4 — Reporting, Totals, Filters & Export

**Goal:** All dashboard data the frontend will later need, served as clean JSON.

- **Owner metrics:** `GET /reports/summary?date=` → `{todays_tickets, todays_sold, arrived_missed}` (the three dashboard containers), per warehouse and combined.
- **Detail feeds:** `GET /reports/arrived-today`, `GET /reports/sold-today` — full rows: ticket ID, item details, stored-where, status, staff.
- **Filters (query params on all list endpoints):** status (`pending|verified|sold|damaged`), date range, warehouse, seller, staff member. Pagination + sorting everywhere.
- **Manager totals:** `GET /reports/stock` → on-hand / reserved / damaged / available per product, per seller, per warehouse (Mongo aggregation pipelines).
- **Export:** `GET /reports/export?format=csv|xlsx` on any filtered view (openpyxl) — Excel is an output, never the database.
- **Migration:** one-off script `scripts/migrate_excel.py` importing the two legacy sheets with validation report + reconciliation flags.

**Exit criteria:** Aggregations verified against seeded fixtures; export files open correctly; migration dry-run report produced.

---

## Phase 5 — Voice Pipeline, Vision Measurement, NL Query & Public API

**Goal:** AI endpoints — but every AI path writes through the SAME service layer as manual entry (no bypass).

- **Voice logging ("Hey Buddy") — backend contract:**
  1. `POST /voice/transcribe` — accepts audio, returns transcript (Whisper local or managed STT behind an interface).
  2. `POST /voice/parse` — LLM extraction of transcript → structured draft `{name, width, height, weight?, fragile, damage?}` with per-field confidence; returned as a **confirmation draft**, saved as `DRAFT` (nothing touches stock).
  3. `POST /voice/drafts/{id}/confirm` — on rookie acceptance, calls the *identical* item-logging service from Phase 2 (same validation, same idempotency, same approval pipeline).
- **Vision measurement:** `POST /vision/measure` — image + reference marker (ArUco of known size) → OpenCV estimates width/height, returned to pre-fill the draft. **Weight always manual.** Confidence + marker-detection failure handled explicitly.
- **Near-duplicate guard:** on item create, fuzzy-match (name + dims + UPC, same day) → 409 with match details unless `force=true` (Manager only).
- **NL stock query:** `POST /query` — natural language → safe, parameterized aggregation (allow-listed query templates only; the LLM selects + fills templates, never writes raw Mongo). RBAC applied to results.
- **Scripting API:** scoped `api_keys` collection (read-only vs read-write scopes), `X-API-Key` auth path, rate limiting — so routine morning checks can be scripted against the same documented endpoints.

**Exit criteria:** Voice draft → confirm → normal pipeline test green; vision returns dims on fixture images; NL query cannot execute anything outside allow-listed templates; API-key auth + scopes tested.

---

## Phase 6 — Hardening, Docs & Handoff to Frontend

**Goal:** Production-ready API the frontend team can build against without asking questions.

- Security pass: rate limiting on auth, token rotation, CORS config (frontend origin placeholder), input-size limits on uploads, dependency audit.
- Backup/restore script + drill for MongoDB; monitoring/health metrics endpoint; structured error catalogue (consistent `{code, message, details}`).
- Test coverage target ≥ 80% on services; load test on reserve endpoint.
- **Frontend handoff pack:** finalized OpenAPI spec, Postman/Bruno collection, seeded demo dataset, `API_GUIDE.md` describing every flow (login → inbox → arrival → approve → store → order → reserve → ship → reports → voice).

**Exit criteria:** All phases' test suites green in CI; handoff pack complete. Only now does frontend work begin.

---

## Phase Order (non-negotiable)

| Phase | Delivers | Blocked by |
|---|---|---|
| 0 | Skeleton, Mongo replica set, ticket generator | — |
| 1 | Auth, Owner→Manager→Staff, RBAC, audit | 0 |
| 2 | Inbox, arrival, ticketing, inspection, storage | 1 |
| 3 | Orders, atomic retrieval, sell | 2 |
| 4 | Reports, totals, filters, export, migration | 3 |
| 5 | Voice, vision, NL query, API keys | 2–4 |
| 6 | Hardening + frontend handoff | all |

**Reminder to agents:** finish and test the current phase before touching the next. No frontend code in this repo. Defer out-of-phase ideas to `BACKLOG.md`.
