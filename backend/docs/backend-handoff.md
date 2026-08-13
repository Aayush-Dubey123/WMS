# Whitfield Fulfillment WMS Backend Handoff Documentation

## 1. System Architecture Overview

The Whitfield Fulfillment Warehouse Management System (WMS) backend is built following **Eigi Backend Standards**, featuring clean multi-tier separation of concerns:

```
              ┌──────────────────────────────────────────────┐
              │           HTTP Clients / Frontend           │
              └──────────────────────┬───────────────────────┘
                                     │ (REST API / JSON)
                                     ▼
              ┌──────────────────────────────────────────────┐
              │         Thin Routes (core/apis/routes)       │
              └──────────────────────┬───────────────────────┘
                                     │ (Call Controllers)
                                     ▼
              ┌──────────────────────────────────────────────┐
              │      Controllers (core/controllers)          │
              │  - Enforce Business Logic & Validation        │
              │  - Manage MongoDB Multi-Doc Transactions     │
              │  - Trigger Audit Log Hooks                   │
              └──────────────┬────────────────┬──────────────┘
                             │                │
                             ▼                ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────────┐
│      CRUDs (core/cruds)              │  │  Services (core/services)        │
│  - MongoDB Motor Queries             │  │  - Audit, Idempotency, Storage   │
│  - ODMantic Models                   │  │  - Voice, Vision (OpenCV), NL    │
└──────────────────┬───────────────────┘  └──────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                  MongoDB Replica Set (Single-Node Transactions)            │
│  - Collections: users, warehouses, inbox_shipments, tickets, items,      │
│                orders, storage_locations, counters, audit_logs,        │
│                voice_drafts, api_keys, idempotency_keys                    │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Inbound & Outbound State Machines

### 2.1 Inbound Ticket State Machine
```
[Seller Pre-Announcement]
         │
         ▼ (POST /inbox/shipments)
      ANNOUNCED
         │
         ▼ (POST /inbox/shipments/{id}/accept)
      ACCEPTED ───────► DECLINED
         │
         ▼ (POST /arrivals - Parcel Scanned)
      ARRIVED (Ticket ID: {WH}-{YYYYMMDD}-{SEQ:03d})
         │
         ▼ (POST /tickets/{id}/items - Idempotent Item Scanning)
PENDING_INSPECTION ◄───► NEEDS_SPEC (Vision / Voice Fill)
         │
         ▼ (PUT /tickets/{id}/submit-inspection)
    INSPECTED (Rookie Submission)
         │
         ▼ (POST /tickets/{id}/approve - Manager Queue)
SHIPMENT_ARRIVED (Approved) / DAMAGED
         │
         ▼ (POST /tickets/{id}/store)
      STORED (Assigned Storage Bin: e.g. A-04-12)
```

### 2.2 Outbound Order State Machine
```
[Order Intake]
       │
       ▼ (POST /orders)
    PENDING
       │
       ▼ (POST /orders/{id}/reserve - Atomic Mongo Transaction: STORED -> RESERVED)
   RESERVED ──────► CANCELLED (POST /orders/{id}/cancel -> Released back to STORED)
       │
       ▼ (POST /orders/{id}/pack - Weight & Dimension Confirmation)
    PACKED
       │
       ▼ (POST /orders/{id}/ship - Outbound Dispatch)
    SHIPPED (Item units transition to SOLD state)
```

---

## 3. Comprehensive Endpoint Inventory

| Category | Method | Path | Auth / Role | Description |
|---|---|---|---|---|
| **Health** | `GET` | `/health`, `/v1/health` | Public | Readiness and database ping check |
| **Auth** | `POST` | `/auth/login` | Public | Obtain JWT Access and Refresh Tokens |
| | `POST` | `/auth/refresh` | Public | Refresh expired access token |
| | `GET` | `/auth/me` | JWT | Get current authenticated user profile |
| **Users** | `POST` | `/users` | OWNER | Create user (Role: MANAGER, STAFF) |
| | `GET` | `/users` | OWNER/MANAGER | List users with filtering |
| | `PUT` | `/users/{id}/deactivate` | OWNER/MANAGER | Deactivate staff and reassign manager units |
| **Warehouses** | `POST` | `/warehouses` | OWNER | Create warehouse facility |
| | `GET` | `/warehouses` | JWT | List warehouse facilities |
| **Inbox** | `POST` | `/inbox/shipments` | JWT | Seller pre-announcement |
| | `POST` | `/inbox/shipments/{id}/accept` | MANAGER | Accept incoming shipment |
| | `POST` | `/inbox/shipments/{id}/decline` | MANAGER | Decline incoming shipment |
| **Arrivals** | `POST` | `/arrivals` | STAFF/MANAGER | Process parcel arrival & yield ticket |
| **Tickets & Scanning** | `POST` | `/tickets/{id}/items` | STAFF | Log scanned item unit (`Idempotency-Key` protected) |
| | `PUT` | `/tickets/{id}/submit-inspection` | STAFF | Submit ticket for manager approval |
| | `POST` | `/tickets/{id}/approve` | MANAGER | Approve ticket inspection |
| | `POST` | `/tickets/{id}/store` | STAFF/MANAGER | Assign storage location bin |
| **Orders & Outbound** | `POST` | `/orders` | JWT | Create customer intake order |
| | `POST` | `/orders/{id}/reserve` | JWT | Atomic stock reservation (MongoDB Transaction) |
| | `GET` | `/orders/{id}/picklist` | JWT | Generate physical bin picklist |
| | `POST` | `/orders/{id}/pack` | JWT | Confirm packed weight and dims |
| | `POST` | `/orders/{id}/label` | JWT | Generate carrier shipping label stub |
| | `POST` | `/orders/{id}/ship` | JWT | Ship order & set items to `SOLD` |
| | `POST` | `/orders/{id}/cancel` | JWT | Cancel reservation & release back to `STORED` |
| **Reports & Export** | `GET` | `/reports/summary` | OWNER/MANAGER | Executive dashboard metrics |
| | `GET` | `/reports/arrived-today` | OWNER/MANAGER | Detail feed of arrived parcels |
| | `GET` | `/reports/sold-today` | OWNER/MANAGER | Detail feed of sold items |
| | `GET` | `/reports/stock` | OWNER/MANAGER | Aggregated stock totals per product |
| | `GET` | `/reports/export` | OWNER/MANAGER | Export reports as `.csv` or `.xlsx` |
| **Voice AI** | `POST` | `/voice/transcribe` | JWT | Transcribe voice audio to text |
| | `POST` | `/voice/parse` | JWT | Extract structured draft via LLM |
| | `POST` | `/voice/drafts/{id}/confirm` | JWT | Confirm draft & write through Phase 2 pipeline |
| **Vision AI** | `POST` | `/vision/measure` | JWT | OpenCV ArUco dimension estimation |
| **NL Search** | `POST` | `/query` | JWT | Safe natural language query search |
| **API Keys** | `POST` | `/api-keys` | OWNER/MANAGER | Generate scoped API key for scripting |
| | `GET` | `/api-keys` | OWNER/MANAGER | List API keys |
| | `DELETE` | `/api-keys/{id}` | OWNER/MANAGER | Revoke API key |

---

## 4. Environment Configuration Matrix

| Variable Name | Default Value | Description |
|---|---|---|
| `APP_NAME` | `Whitfield Fulfillment WMS` | Application display title |
| `APP_VERSION` | `1.0.0` | API version string |
| `DEBUG` | `False` | Debug mode toggle |
| `DATABASE_URI` | `mongodb://localhost:27017/whitfield_wms?replicaSet=rs0` | MongoDB connection URI |
| `DATABASE_NAME` | `whitfield_wms` | MongoDB database name |
| `SECRET_KEY` | `super-secret-key-change-in-production` | Secret key for JWT signing |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT access token TTL in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | JWT refresh token TTL in days |
| `UPLOAD_DIR` | `uploads` | Local directory for static inspection images |

---

## 5. Operational Runbook

### 5.1 Bootstrapping Owner Account
Run seed script:
```bash
python scripts/seed_owner.py
```
Default Credentials created:
- Email: `owner@whitfield.com`
- Password: `Password123!`

### 5.2 Running Legacy Excel Inventory Migration
Run migration script with target warehouse code:
```bash
python -m scripts.migrate_excel path/to/legacy_sheet.xlsx --warehouse RNO
```

### 5.3 Exporting Postman Collection
Export fresh Postman Collection from OpenAPI schema:
```bash
python -m scripts.export_postman_collection
```

### 5.4 Running Pytest Test Suite
Execute full automated integration test suite:
```bash
python -m pytest tests/
```

---

## 6. Production Hardening Checklist

- [x] **Database Transactions**: Single-node MongoDB Replica Set (`rs0`) initialized for multi-document ACID transactions.
- [x] **Authentication Security**: Direct bcrypt password hashing and JWT authorization token verification.
- [x] **Idempotency Locks**: Header `Idempotency-Key` locked in MongoDB to prevent double scanning.
- [x] **Audit Trail**: Automated mutation logging for write actions across system.
- [x] **Anti-Overselling**: Atomic reservation transaction handling with 409 Conflict rejection on concurrent unit claims.
- [x] **Non-Bypass AI Architecture**: Voice and vision endpoints write through the exact same Phase 2 item logging service layer.
- [x] **Safe NL Aggregations**: Allow-listed MongoDB aggregation templates for natural language queries.
- [x] **Export Flexibility**: Server-side `.csv` and `.xlsx` generation using OpenPyXL.
