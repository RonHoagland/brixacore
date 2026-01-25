# BrixaWares – Technology Stack & Architecture (Lite)(V1)

## 1. Purpose of This Document

This document defines the **official, authoritative technology stack** for BrixaWares.

It exists to:

- Lock the Lite stack decisions
- Explain **why** each technology was chosen
- Define **how** each part of the stack is intended to be used
- Prevent architectural drift and accidental over‑engineering
- Clearly separate **Lite (locked)** from **Pro (open)** decisions

This document is intended to be **lockable** and referenced by all future technical, functional, and installer documentation.

---

## 2. Core Product Constraints

The stack must support the following non‑negotiable constraints:

- On‑premise deployment (no cloud dependency)
- Minimal technical skill required by end users
- LAN‑accessible, browser‑based UI
- HTTPS required (modern browser enforcement)
- Simple reporting via list views (Lite)
- CSV export only in Lite
- First‑class session, audit, and event logging
- Predictable filesystem‑based document storage
- One‑step installer experience (wizard‑based)

---

## 3. Lite Version – Locked Technology Stack

### 3.1 High‑Level Summary (Lite)

| Layer         | Technology              | Status |
| ------------- | ----------------------- | ------ |
| Language      | Python                  | LOCKED |
| Web Framework | Django                  | LOCKED |
| Frontend      | Django Templates + HTMX | LOCKED |
| Database      | PostgreSQL              | LOCKED |
| Deployment    | Windows LAN Server      | LOCKED |
| Protocol      | HTTPS only              | LOCKED |
| Packaging     | Single Installer Wizard | LOCKED |

---

### 3.2 Backend

**Django (Python)** is used as a monolithic backend framework.

**Why Django:**

- Mature, stable, long‑term support ecosystem
- Built‑in authentication, permissions, admin tooling
- Native migration system
- Strong ORM reduces custom SQL risk
- Ideal for rapid development with clear structure

**How Django is used:**

- Server‑rendered application (not API‑first)
- Handles authentication, authorization, and sessions
- Manages schema via migrations
- Emits audit and event logs at the application layer

---

### 3.3 Frontend

**Django Templates + HTMX**

**Why:**

- Minimal JavaScript footprint
- No SPA complexity
- Faster development
- Easier debugging in on‑prem environments
- Excellent UX without frontend framework overhead

**Usage Pattern:**

- Object‑first navigation
- List View → Record View → Related Tabs
- Filters and searches act as reports
- HTMX used only for partial updates (tables, modals, inline edits)

---

### 3.4 Database

**PostgreSQL (bundled)**

**Why:**

- Highly reliable and well supported
- Strong transactional guarantees
- Widely accepted in enterprise environments
- Suitable for embedded/bundled installation

**Usage:**

- Bundled and installed by the Lite installer
- Database schema fully managed by Django migrations
- No direct user interaction with the DB required

---

## 4. Networking & Security (Lite)

### 4.1 LAN Server Model

- One Windows machine hosts the application
- Other users access via browser over the LAN
- No cloud connectivity required

### 4.2 HTTPS Enforcement

- HTTPS is mandatory
- Installer generates a local TLS certificate
- HTTP access is disabled

**Installer responsibilities:**

- Generate or install local certificate
- Bind HTTPS to configured port
- Configure Django to enforce HTTPS
- Create Windows Firewall rule

**User Experience:**

- Initial certificate warning explained in plain language
- LAN URLs displayed clearly:
  - [https://localhost\:PORT](https://localhost\:PORT)
  - [https://MACHINE-NAME\:PORT](https://MACHINE-NAME\:PORT)
  - [https://LAN-IP\:PORT](https://LAN-IP\:PORT)

---

## 5. Installation & Packaging Strategy (Lite)

### 5.1 Installer Goals

- One continuous wizard
- No terminal usage
- No manual dependency installation
- Safe defaults with minimal choices

### 5.2 Wizard Options

- Typical vs Custom install
- Install path
- Data/document root path
- HTTPS port (with conflict detection)
- Admin account creation
- Start on boot (Yes/No)

### 5.3 Installer Actions (Behind the Scenes)

- Install packaged Python runtime
- Install and configure PostgreSQL
- Create database and run migrations
- Configure application settings
- Register Windows Service
- Configure firewall
- Create desktop shortcut

---

## 6. Files, Documents & Storage

- Files stored on filesystem (not in DB)
- Base storage path defined in Preferences
- Subfolders automatically created per object/table
- Predictable, human‑readable structure

---

## 7. Reporting & Exports (Lite)

- Reporting implemented via List Views
- Filters and search act as reports
- Export formats:
  - CSV only
- Browser print used for hard copies

---

## 8. Sessions, Audit & Event Logging

- Sessions recorded on login
- User identity captured at session start
- All critical actions emit audit events
- Delete operations always record target ID
- Failures always include reason
- Retention limits configurable via Preferences

---

## 9. Core Libraries

### 9.1 Locked Core Dependencies

- Django
- HTMX
- PostgreSQL driver (psycopg)
- Django migrations
- Built‑in Django auth

### 9.2 Optional / Pluggable (Not Lite‑Critical)

- Background job frameworks
- PDF generation libraries (Pro only)
- External authentication providers

---

## 10. Pro Version – Open Decisions

The following are intentionally **not locked**:

- Database engine
- Frontend complexity (SPA vs server‑rendered)
- Job queue architecture
- Advanced export formats
- Deployment and scaling strategies

These will be decided in a future Pro‑specific architecture document.

---

## 11. Status

**Lite Stack:** READY TO LOCK

This document represents the authoritative technical baseline for the Lite version of BrixaWares.

