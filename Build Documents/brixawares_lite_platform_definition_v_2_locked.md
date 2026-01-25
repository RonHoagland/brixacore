# BrixaWares – Lite Platform Definition (V2 – Locked)

> **Purpose**: Define exactly what the **Lite Platform** is, what modules and editions it contains, what data objects (tables) exist at a high level, and the rules that keep Lite buildable fast.
>
> **Status**: **V2 LOCKED** — Scope-defining document. Field-level definitions are intentionally excluded and handled in separate **Model Documents**.

---

## 1) Product Summary

### What Lite is
**BrixaWares Lite** is a **desktop application** designed for extra-small businesses.

Lite is a single platform that supports **module toggles** (on/off) governed by licensing entitlements.

Lite application modules:
- **Sales**
- **Invoice**
- **Service**
- **Projects**
- **Full** (all modules included)

Lite also offers an edition called **Full**, which enables **all** Lite application modules.

### Lite vs Pro
- **Lite and Pro are different architectures and separate products.**
  - **Lite** is a desktop app.
  - **Pro** is a web-based system designed for larger infrastructures.
- Lite and Pro share **PostgreSQL** as the database engine.
- Lite and Pro may use **different schemas**; data migration is handled through explicit mapping (defined outside this document).

### What Lite is not
Lite is intentionally **shallow**:
- minimal workflows
- minimal automation
- minimal reporting (list views)
- no complex relationship-driven timelines unless explicitly linked via context

---

## 2) Architecture: Core Utilities, Base Modules, Application Modules

### 2.1 Core Utilities
**What it is**: universal platform utilities. **No business objects.**

Examples:
- Users, roles/permissions
- Sessions + system-wide event/audit logging
- Preferences
- Backup/restore
- File/document storage plumbing (paths, retention)
- Scheduler/job runner (if any)
- Import/export, printing
- Diagnostics, app updates (if applicable)
- Licensing activation + entitlement checks

**Rule**: Core Utilities never depend on Base Modules or Application Modules. Everything else can depend on Core.

### 2.2 Base Modules
**What it is**: shared business objects that every Lite edition needs.

Includes (Lite):
- Clients
- Contacts *(via People in the background)*
- People *(background only)*
- Addresses
- Phones
- Notes + Documents
- Products *(Lite view of Inventory; catalog behavior)*
- ValueLists

**Rule**: Application Modules can depend on Base Modules. Base Modules do **not** depend on Application Modules.

### 2.3 Application Modules
**What it is**: the business modules customers buy and enable.

**Rule**: Application Modules can:
- reference Base tables via FK
- extend Base screens via extension points (tabs/widgets/actions)
- register screens/nav items only when entitled

---

## 3) Editions (What Customers Buy)

### 3.1 Lite Editions
All Lite editions include **Core Utilities + Base Modules**.

- **Lite Sales** = Core + Base + Sales
- **Lite Invoice** = Core + Base + Invoice
- **Lite Service** = Core + Base + Service
- **Lite Projects** = Core + Base + Projects
- **Lite Full** = Core + Base + Sales + Invoice + Service + Projects

### 3.2 Module upgrades inside Lite (Locked)
- Users can purchase one edition initially and **add modules later** (entitlements turn on).
- **Full** is a hard bundle: it always includes all Lite application modules.

---

## 4) Lite Modules (Application Modules)

### 4.1 Service (Lite)
**Goal**: Track service execution and get paid.

**Includes**
- Clients
- Contacts *(via People in the background)*
- Products (Lite catalog)
- Service Items
- Work Orders
- Work Order Items (parts + labor)
- Invoices *(simple, for payment attachment and Pro alignment within Lite)*
- Payments *(attached to invoices only)*
- Notes + Documents

**Excludes**
- Opportunities
- Interactions (beyond Notes)
- Full inventory/procurement (receiving, locations, transfers)

### 4.2 Sales (Lite)
**Goal**: Capture prospects and generate quotes.

**Includes**
- Clients
- Contacts *(via People)*
- Leads
- Products
- Quotes
- Quote Lines
- Notes + Documents

**Excludes**
- Payments
- Invoices
- Work Orders
- Service Items
- Opportunities
- Interactions (beyond Notes)

### 4.3 Invoice (Lite)
**Goal**: Issue invoices and track payments.

**Includes**
- Clients
- Products
- Invoices
- Invoice Lines
- Payments
- Notes + Documents

**Excludes**
- Quotes
- Contacts (beyond a simple selection)
- Work Orders
- Service Items

### 4.4 Projects (Lite)
**Goal**: Basic internal project/task tracking.

**Includes**
- Projects
- Tasks
- Epics *(hidden in Lite; one per project)*
- Notes + Documents

**Excludes**
- Epic management UI
- Time tracking
- Dependencies / advanced planning features

---

## 5) Core Design Rules (Locked)

### 5.1 Epics are hidden in Lite
- Epics exist in the database.
- In Lite, the system creates **exactly one Epic per Project** named **“General”**.
- **All Tasks belong to that Epic**.
- Epics are **never visible** to end users in Lite.

### 5.2 Clients in Lite
- Lite uses the term **Clients** to represent external entities.
- Leads represent pre-customer intake.

### 5.3 People table is background-only in Lite
- People is **never exposed** in Lite UI.
- Lite uses **1:1** links:
  - People ↔ Contact
  - People ↔ Employee/User

### 5.4 Inventory is called Products in Lite
- The underlying table may be named Inventory.
- The Lite UI uses the label **Products**.
- Lite treats Products as a **catalog** (no procurement, no multi-location stock logic).

### 5.5 Addresses (Lite)
- Lite includes an **Addresses** table owned by **Clients**.
- Address types supported in Lite:
  - **Billing**
  - **Shipping**
- A Client may have:
  - **1 Billing address**
  - **0–1 Shipping address**
- Addresses are selectable on:
  - Invoices (**Billing required**)
  - Quotes (optional)
  - Work Orders (optional)

### 5.6 Phones (Lite)
- Phones table is used to store phone numbers.
- Lite UI enforces:
  - **max 2 phone numbers per Client**
  - **max 2 phone numbers per Contact**

---

## 6) Invoices & Payments (Lite Rules)

### 6.1 Payments always attach to Invoices
- Payments are recorded against an **Invoice** (required).
- If the user is working from a Work Order, the Work Order references an Invoice.

### 6.2 Work Orders and Invoices
- Work Orders may exist without an Invoice initially.
- **When a Work Order is marked Completed/Closed, the system automatically creates an Invoice** if one does not already exist.
- Work Order screens show the invoice status/balance; users may still work primarily in Work Orders.

### 6.3 Invoice simplicity rules

**Statuses (Lite)**
- Draft
- Issued
- Paid
- Void

**Automatic status behavior (Lite)**
- New invoices are created as **Draft**.
- When an invoice is explicitly sent/posted, status becomes **Issued**.
- When total applied payments are **≥ invoice total**, status becomes **Paid** automatically.
- If an issued invoice is cancelled, status becomes **Void**.

**Line item rules**
- **Everything is a line item except tax.**
- Shipping, discounts, surcharges, fees = line items.
  - Discounts are negative line items.

---

## 7) Notes & Documents (Reusable + Context Rollups)

### 7.1 Objective
Provide **one reusable widget** that can be placed on any top-tier screen without building custom Notes/Documents CRUD per module.

### 7.2 Linking model
- A Note/Document can link to **1–5 entities**.
- Rollup is based on **context provided by the calling screen** (explicit IDs), not automatic relationship discovery.

### 7.3 Tables (high level)
- Notes + NoteLinks
- Documents + DocumentLinks

---

## 8) Table List (Lite)

### 8.1 Core Utilities (non-business)
- Users
- Roles
- UserRoles
- Preferences
- Sessions
- Event/Audit Logs
- Licensing
- Backup/Restore metadata
- Scheduler/Jobs (if any)

### 8.2 Base Modules
- Clients
- Addresses
- Contacts
- People *(background only; 1:1 to Contacts and Users)*
- Phones *(max 2 per Client and 2 per Contact)*
- Products *(Inventory table, exposed as Products in UI)*
- Notes
- NoteLinks
- Documents
- DocumentLinks
- ValueLists

### 8.3 Application Modules
**Sales**
- Leads
- Quotes
- QuoteLines

**Invoice**
- Invoices
- InvoiceLines
- Payments

**Service**
- ServiceItems
- WorkOrders
- WorkOrderItems

**Projects**
- Projects
- Epics *(hidden; one “General” per Project)*
- Tasks

---

## 9) Reporting (Lite)
- Reports are implemented as **List Views + Filters + Search**.
- Export from list views: **CSV only**.
- Printing via browser print.

---

## 10) Decisions (Locked)
- Lite editions include **Core Utilities + Base Modules**.
- Application modules are enabled by entitlement.
- **Full** is a hard bundle (all Lite application modules included).
- Lite customers can **add modules later** via licensing/entitlements.
- Field-level definitions belong in **Model Documents**.

