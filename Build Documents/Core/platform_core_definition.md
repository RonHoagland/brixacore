# Platform Core Definition

## Purpose
The **Platform Core** defines the shared, non-negotiable foundation used by **all applications** built in this ecosystem. It is not a business application, and it does not contain business-domain entities. Its sole purpose is to provide the infrastructure, conventions, and services that every application relies on.

This Core is built **once**, maintained carefully, and extended only through well-defined modules layered on top.

---

## What the Platform Core *Is*
The Platform Core is:
- Infrastructure, not business logic
- Shared by every application
- Required regardless of application type
- Stable, opinionated, and intentionally boring

If an application could not reasonably function without a capability, that capability belongs in the Core.

---

## What the Platform Core *Is Not*
The Platform Core does **not** include:
- Business-domain entities (Clients, Products, Invoices, Inventory, etc.)
- Workflow or operational logic
- Industry-specific concepts
- Features that only some applications require

Those live in **modules**, even if some modules are commonly enabled.

---

## Core Design Principles

1. **Separation of Concerns**  
   The Core provides mechanisms and rules. Modules provide meaning and behavior.

2. **Consistency Over Flexibility**  
   The Core enforces patterns so modules behave predictably and integrate cleanly.

3. **Explicit Over Clever**  
   Avoid abstract data models that trade short schemas for long-term confusion.

4. **Scalable by Convention**  
   Growth is handled through standard patterns, not special cases.

---

## Platform Core Components

### 1. Application Shell
Provides the structural container for all applications.
- Layout system
- Navigation framework (modules register themselves)
- Routing
- Standard list view framework (filtering, sorting, searching)
- Standard detail view framework
- Global search framework (pluggable by modules)

---

### 2. Identity & Access Control
Defines who can access the system and what they are allowed to do.
- Users
- Roles
- Permissions
- Authentication (login/logout)
- Session tracking

---

### 3. System Configuration
Centralized control of system behavior.
- Global preferences
- Value list framework (user-editable dropdown sources)
- Feature flags / licensing toggles
- Environment configuration (paths, limits, switches)

---

### 4. Persistence & Metadata Standards
Enforced conventions applied to all data entities.
- UUID primary keys
- Created / updated timestamps
- Created_by / updated_by
- Optional soft-delete support

These standards ensure consistency across all modules.

---

### 5. Status & Lifecycle Framework
Provides a generic mechanism for managing record state.
- State fields
- Valid state transitions
- Locked states
- Transition logging

The framework exists in Core; actual states are defined by modules.

---

### 6. Numbering & Identity Services
Central service for human-readable identifiers.
- Configurable numbering rules
- Prefix / year / sequence support
- Collision prevention
- Object-type awareness

Modules opt in as needed.

---

### 7. File & Binary Storage Infrastructure
Infrastructure for storing and referencing files.
- Storage path management
- Retention rules
- Attachment references
- No business meaning implied

---

### 8. Audit & Event Logging
Minimal but reliable system-level visibility.
- Login / logout events
- Create / update / delete events
- Status transitions
- Permission changes

---

### 9. Background Services Framework
Supports asynchronous and scheduled operations.
- Job scheduler
- Background task execution
- Locking to prevent duplicate runs
- Error and retry handling

---

### 10. Reporting Mechanism (Infrastructure Only)
Provides the plumbing for data visibility.
- List-based reporting framework
- Filtering and search persistence
- CSV export support
- Browser-based printing

No predefined business reports exist in Core.

---

## Relationship to Modules
All business functionality is implemented as **modules** layered on top of the Platform Core.

Examples of modules:
- Clients & Contacts
- Notes & Documents
- CRM
- Service Management
- Inventory
- Invoicing
- Procurement

Some modules may be enabled in all products, but they remain modules by design.

---

## Core Rule of Inclusion
A capability belongs in the Platform Core **only if every application requires it to function**.

If the answer is anything other than an unqualified "yes", it belongs in a module.

---

## Outcome
This approach ensures:
- A stable, reusable foundation
- Faster development of new applications
- Consistent behavior across products
- Reduced long-term maintenance and technical debt

The Platform Core is intentionally minimal, rigid, and dependable.

