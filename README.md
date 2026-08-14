# Whitfield Fulfillment - Warehouse Management System (WMS)

> **Purpose:** Eigi - WMS Software Solution  
> **Author:** Aayush Dubey  
> **Client Request:** EIGI.AI Case Study — Whitfield Fulfillment (Reno, NV & Columbus, OH)  
> **Tech Stack:** FastAPI (Python 3.11+), MongoDB (Replica Set `rs0`), React 18, Vite, TypeScript, Tailwind CSS, TanStack Query  

---

## 📌 Executive Summary & Client Background

**Whitfield Fulfillment**, operated by Dan Whitfield, runs two key fulfillment hubs located in **Reno, Nevada** and **Columbus, Ohio**. Small and mid-sized e-commerce sellers store their inventory at whichever warehouse is geographically closer, and Whitfield's team manages receiving, storage, picking, packing, weighing, and shipping.

### The Problem (Legacy Excel System)
Prior to this system, Whitfield Fulfillment relied on manual Excel spreadsheets to track inventory and order processing. As business scaled, severe operational vulnerabilities emerged:
* **Duplicate Stock Entries & Data Corruption:** Laptop freezes during receiving resulted in duplicate entries (e.g., doubling actual stock for 3 products, taking managers a full day to diagnose).
* **Inventory Race Conditions & Over-selling:** Concurrent spreadsheet edits by multiple team members led to double-booking sold-out stock (e.g., two sellers receiving confirmation for the same 9 remaining units).
* **Zero Auditability:** Excel provided no history or traceability for manual edits ("who changed this number?").
* **Outbound Bottlenecks:** Order pulling, packing, box measurement, and label printing lagged by 1–2 days.
* **Security & Access Control Risk:** Expanding staff required granular permissions so newer hires could not view or modify sensitive data reserved for trusted managers/owners.
* **Physical Constraints:** Desk workers scanning UPC barcodes with handheld scanners needed hands-free interactions (voice controls) rather than typing into a laptop.

---

## 🎯 Solution Architecture & Key Features

To address Dan Whitfield's requirements, the **Eigi - WMS Software** was built from the ground up as an enterprise-grade, real-time, role-secured warehouse management solution with built-in AI assistance and voice/vision controls.

```
                  ┌─────────────────────────────────────────────────────────┐
                  │                 Eigi - WMS Software                     │
                  └────────────────────────────┬────────────────────────────┘
                                               │
       ┌──────────────────────────────┬────────┴──────────────┬──────────────────────────────┐
       │                              │                       │                              │
┌──────┴──────────────┐    ┌──────────┴───────────┐    ┌──────┴──────────────┐    ┌──────────┴───────────┐
│ Multi-Warehouse     │    │ Concurrency & ACID   │    │ Role-Based Access   │    │ AI & Voice/Vision    │
│ Operations          │    │ Inventory Management │    │ Control (RBAC)      │    │ Intelligence         │
├─────────────────────┤    ├──────────────────────┤    ├─────────────────────┤    ├──────────────────────┤
│ • Reno, NV Facility │    │ • MongoDB rs0        │    │ • OWNER             │    │ • Hands-free Voice   │
│ • Columbus, OH      │    │   Transactions       │    │ • MANAGER           │    │   Commands (STT)     │
│ • Real-time Sync    │    │ • Atomic Ticket Gen  │    │ • STAFF             │    │ • Vision Inspection  │
│ • Consolidated View │    │ • Race Condition Pro │    │ • API Key Scripts   │    │ • Natural Language AI│
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘    └──────────────────────┘
```

---

## 🚀 Built Capabilities & System Features

### 1. 🔒 Role-Based Access Control (RBAC) & Security
* **Tiers:** `OWNER`, `MANAGER`, and `STAFF`.
* **Security Enforcement:** JWT Bearer Token authentication with role dependencies (`commons/auth.py`).
* **Granular Navigation:** Navigation menu and API endpoints dynamically adapt to user permissions.
  * **OWNER:** Full system control, warehouse configuration, user role management, system audits.
  * **MANAGER:** Inventory control, approval workflows, report generation, user views.
  * **STAFF:** Receiving desk logging, order picking/packing, voice commands, status updates.

### 2. 📦 Inbound Receiving & Ticket Management
* **Atomic Sequential Ticket Generation:** Auto-generates unique IDs (`WH-REC-2026-XXXX`) using MongoDB counter locks to ensure zero duplicate reference numbers.
* **UPC Barcode Scanning & Condition Logging:** Desk staff can scan barcodes, set incoming item counts, and record item conditions (e.g., damaged vs. good stock).
* **Carrier Tracking & Drop-off Tickets:** Logs carrier tracking numbers or manual drop-off tickets.

### 3. ⚡ Outbound Fulfillment & Concurrency Control
* **ACID Transactions:** Built on MongoDB single-node replica set (`rs0`) with multi-document transaction support to guarantee zero over-selling or race conditions.
* **Order Pipeline:** Tracks orders through `PENDING` ➔ `PICKING` ➔ `PACKED` ➔ `SHIPPED`.
* **Box Measurement & Labeling Workflow:** Streamlines box weight and dimension logging to minimize the 1-2 day outbound delay.

### 4. 📜 Immutable Audit Trail & History
* **Full Accountability:** Every inventory adjustment, order status update, ticket creation, and system login is recorded in an immutable audit ledger.
* **Audit Metadata:** Captures `timestamp`, `user_id`, `facility_id`, `action`, `target_collection`, `old_value`, and `new_value`.

### 5. 🤖 AI Assistant, Voice & Vision Services
* **Hands-Free Voice Commands:** Speech-to-Text (STT) integration enabling warehouse floor staff to log received items or query stock verbally while scanning boxes.
* **Computer Vision Inspection:** Upload images of incoming packages or damaged items for automated visual verification.
* **Natural Language Query Bot:** AI query assistant that answers stock availability and order questions in plain English without requiring manual spreadsheet lookups.
* **Automated Worker Scripting:** API key generation allowing tech-savvy staff to write automated Python/Shell scripts for morning routine checks.

### 6. 📊 Legacy Excel Data Migration
* **Built-in Migration Tool (`migrate_excel.py`):** Automatically ingests legacy Excel sheets, parses product rows, normalizes stock counts, and seeds MongoDB cleanly without data loss.

---

## 🛠️ Project Structure

```
WMS/
├── backend/                        # FastAPI Python Server
│   ├── main.py                     # Entry point (uvicorn runner)
│   ├── core/
│   │   ├── apis/
│   │   │   ├── api.py              # Root FastAPI application & middleware
│   │   │   ├── routes/             # 16 domain routers (auth, facility, order, ticket, voice, vision, etc.)
│   │   │   └── schemas/            # Pydantic request/response schemas
│   │   ├── controllers/            # Business logic & ACID database transactions
│   │   ├── cruds/                  # Motor MongoDB CRUD data access handlers
│   │   ├── database/               # Database setup, connection pooling, init_db scripts
│   │   ├── models/                 # MongoDB collection document models
│   │   ├── services/               # External AI integrations (LLM, Voice STT, Vision)
│   │   └── utils/                  # Atomic generators & utilities
│   ├── commons/                    # JWT authentication, logging, custom exceptions
│   ├── scripts/                    # Legacy Excel migration & owner seeding scripts
│   ├── tests/                      # Pytest suite (Phase 01, Phase 02+, Smoke tests)
│   └── requirements.txt            # Backend Python dependencies
├── frontend/                       # React + Vite TypeScript Client
│   ├── src/
│   │   ├── components/             # UI components & Shadcn/Radix primitives
│   │   ├── lib/                    # Auth Context, API Client (48+ endpoints), Route Protection
│   │   └── routes/                 # TanStack Router pages (Dashboard, Orders, Tickets, Login, etc.)
│   ├── package.json                # Frontend NPM dependencies & scripts
│   └── vite.config.ts              # Vite configuration
└── README.md                       # Master Documentation File
```

---

## 🚦 Getting Started & Local Setup

### Prerequisites
* **Python:** 3.11+
* **Node.js:** 18+ & npm / bun
* **MongoDB:** 6.0+ configured as a single-node replica set (`rs0`) for transaction support.

---

### Backend Setup

1. **Navigate to the backend folder:**
   ```bash
   cd backend
   ```

2. **Set up virtual environment & install dependencies:**
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On Linux/macOS:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Configure Environment Variables (`backend/.env`):**
   ```env
   PORT=8000
   MONGO_URI=mongodb://localhost:27017/?replicaSet=rs0
   MONGO_DB_NAME=wms_db
   JWT_SECRET=your-secret-key-here
   JWT_ALGORITHM=HS256
   ```

4. **Initialize Database Collections & Indexes:**
   ```bash
   python -m core.database.init_db
   ```

5. **Run Database Seeding / Migration (Optional):**
   ```bash
   # Seed default owner account
   python scripts/seed_owner.py

   # Migrate legacy Excel sheets
   python scripts/migrate_excel.py
   ```

6. **Start Backend Dev Server:**
   ```bash
   python main.py
   # OR
   uvicorn main:app --reload --port 8000
   ```
   * **API Base URL:** `http://127.0.0.1:8000`
   * **Swagger Docs:** `http://127.0.0.1:8000/docs`

---

### Frontend Setup

1. **Navigate to the frontend folder:**
   ```bash
   cd ../frontend
   ```

2. **Install Dependencies:**
   ```bash
   npm install
   ```

3. **Start Frontend Dev Server:**
   ```bash
   npm run dev
   ```
   * **App URL:** `http://localhost:5173`

---

## 🧪 Testing & Verification

### Running Backend Tests
The backend includes extensive test coverage across authorization, inbound workflow, order processing, concurrency locks, and AI endpoints:

```bash
cd backend

# Run entire test suite
python -m pytest -q

# Run Phase 01 Tests (Auth, RBAC, Ticket Generator)
python -m pytest tests/phase01/ -q

# Run Phase 02+ Tests (Inbound, Concurrency, Orders, AI Services)
python -m pytest tests/phase02plus/ -q

# Run Smoke Tests
python -m pytest tests/smoke/ -q
```

---

## 📋 API Route Summary

The backend exposes over 48+ RESTful endpoints organized into 16 distinct domain routers:

| Router | Path Prefix | Description |
| :--- | :--- | :--- |
| **Auth** | `/auth` | Authentication, JWT login, token validation |
| **User** | `/users` | User management & role assignment (`OWNER`, `MANAGER`, `STAFF`) |
| **Facility** | `/warehouses` | Facility management (Reno, NV & Columbus, OH) |
| **Arrivals** | `/arrivals` | Inbound shipments receipt & tracking |
| **Tickets** | `/tickets` | Ticket creation, barcode lookup, status updates |
| **Approvals** | `/approvals` | Manager review & ticket approval workflows |
| **Orders** | `/orders` | Outbound order allocation, status pipeline, packing |
| **Storage** | `/storage` | Warehouse bin & shelf inventory placement |
| **Audit** | `/audit` | Query immutable user action and inventory logs |
| **Reports** | `/reports` | Warehouse stock reports, shipping metrics |
| **Voice** | `/voice` | Speech-to-Text hands-free command processing |
| **Vision** | `/vision` | Image upload & damage inspection AI |
| **Query** | `/query` | Natural language AI query assistant |
| **API Keys** | `/api-keys` | Scripting key generation for automated background workers |
| **Inbox** | `/inbox` | Real-time system notifications & alerts |
| **Health** | `/health` | Server & MongoDB replica set health status |

---

## 👤 Project Metadata

* **Author:** Aayush Dubey  
* **System Name:** Eigi - WMS Software  
* **Client Reference:** Whitfield Fulfillment (EIGI.AI Case Study)  
