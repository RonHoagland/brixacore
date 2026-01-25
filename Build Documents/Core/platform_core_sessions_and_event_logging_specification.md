# Platform Core - Sessions and Event Logging (System Wide) Specification

## Purpose

The **Sessions and Event Logging (System Wide)** component defines how the system records user sessions and system events for accountability, troubleshooting, and auditing.

This is a **Core** capability and applies to every application and module.

This document defines **what must be built** and **how it must behave**, without prescribing implementation code.

---

## Scope

This document covers:
- Session logging (top-level Sessions table)
- User transaction/event logging (create/delete events for v1)
- Required event fields and structure
- Event generation rules
- Retention and immutability rules
- Query and reporting expectations for admin usage

This document does **not** cover:
- Business analytics
- Full field-change history/versioning
- Real-time monitoring/alerting
- Non-user/system-to-system events (unless explicitly added later)

---

## Core Principles

1. **System Wide and Consistent**  
   Every module uses the same session and event logging mechanisms.

2. **Append-Only**  
   Sessions and transaction logs are immutable once written.

3. **Minimum Useful Data**  
   Capture enough to explain who did what and when, without becoming a data warehouse.

4. **Fail Safe**  
   Logging failures must not silently pass.

---

## 1) Sessions (Top-Level)

### Purpose
A **Session** record represents an authentication attempt and (if successful) the resulting authenticated user session.

A new session record is created on every login attempt (successful or failed).

### Session Record Creation
- Created on every authentication attempt.
- Linked to the authenticated user when authentication succeeds.
- A successful session remains active until logout or expiration.

### Sessions Table (Required Fields)
- `id` (UUID, PK)
- `user_id` (UUID, FK to Users, nullable)
  - Required when authentication succeeds
  - Null when authentication fails and no user could be resolved
- `attempted_username` (string, nullable)
  - Captures what was entered at login; required when `user_id` is null
- `auth_result` (enum/string)
  - Allowed values (v1): `success`, `failure`
- `auth_failure_reason` (string, nullable)
  - Required when `auth_result = failure`
  - Examples: invalid_credentials, inactive_user, locked_out (if later), other
- `started_at` (datetime)
- `ended_at` (datetime, nullable)
- `end_reason` (enum/string, nullable)
  - Allowed values (v1): `logout`, `timeout`, `admin_invalidate`, `auth_failure`
- `client_info` (string, nullable) — user agent or equivalent
- `ip_address` (string, nullable)

### User Snapshot at Login
On successful authentication, the session must capture a snapshot of user information at login.

- `user_snapshot` (text/JSON)
  - Minimum contents:
    - user_id
    - username
    - display_name
    - active/inactive status
    - **roles assigned to the user at login**

> Note: This snapshot is for historical traceability. It does not replace runtime permission checks.

### Session Behavior
- `started_at` is set once.
- For successful sessions:
  - `ended_at` and `end_reason` are set only when the session ends.
- For failed sessions:
  - `end_reason` must be `auth_failure`
  - `ended_at` must be set immediately (same transaction as creation)

### Session Immutability
- Session records are append-only.
- The only allowed update for successful sessions is setting `ended_at` and `end_reason` when the session ends.

---

## 2) User Transactions (Event Logging) (Event Logging)

### Purpose
The **User Transaction** table records discrete user-triggered system events.

**V1 Scope:** record **Create** and **Delete** operations only.

### User Transaction Record Creation
A transaction record is created when:
- A record is created (successful commit)
- A record is deleted (successful commit)

### User Transactions Table (Required Fields)
- `id` (UUID, PK)
- `session_id` (UUID, FK to Sessions)
- `user_id` (UUID, FK to Users) — duplicated for query convenience
- `event_ts` (datetime)
- `event_type` (enum/string)
  - Allowed values (v1): `create`, `delete`
- `entity_type` (string)
  - The logical entity/table name (e.g., Client, Contact, Invoice)
- `entity_id` (UUID)
  - The UUID of the record created or deleted
- `reason_text` (string, nullable)
  - Used when a delete requires a reason (module-defined rule)
- `summary` (string, nullable)
  - Short human-readable description (optional)

### Transaction Behavior
- Transactions are written only after a successful database commit.
- Transactions must reflect the final outcome (no “attempted” events in v1).

### Immutability
- User Transaction records are append-only and must not be edited or deleted by standard users.

---

## 3) Enforcement Rules

### Required Logging Coverage (V1)
- Every successful create operation must generate a `create` transaction.
- Every successful delete operation must generate a `delete` transaction.
- For delete events:
  - The `entity_id` of the record being deleted must always be recorded.
  - Some entities may require `reason_text` (module-defined rule). If required and missing, the delete must be denied.

### No Bypass Rule
- Modules must not bypass Core logging.
- Any create/delete path must flow through a Core mechanism that ensures logging.

### Failure Rules
- If event logging fails, the system must:
  - Fail the operation (fail closed), OR
  - Queue the log write for guaranteed persistence

**Locked for v1:** fail closed (operation fails if the log cannot be written).

---

## 4) Retention

### Default Retention
- Sessions and User Transactions are retained indefinitely by default.

### Purge Policy (Optional Later)
- A configurable purge policy may be added later.
- Purging must be restricted to administrators and must itself be logged.

---

## 5) Administrative Query Requirements

Admins must be able to query:
- Sessions by user, date range, active vs ended
- User Transactions by user, date range, event type
- User Transactions by entity type and entity id

Query patterns must be index-friendly.

---

## 6) Indexing Requirements

### Sessions
- Index on `user_id`
- Index on `started_at`
- Index on `ended_at`

### User Transactions
- Index on `session_id`
- Index on `user_id`
- Index on `event_ts`
- Composite index on (`entity_type`, `entity_id`)
- Index on `event_type`

---

## Acceptance Criteria (Sessions & Logging)

- A session record is created on every login attempt (success or failure).
- Failed login sessions include an `auth_failure_reason` and are ended immediately.
- Successful sessions are ended on logout/timeout/admin invalidate.
- A user snapshot is stored on successful login.
- Every successful create generates a `create` transaction.
- Every successful delete generates a `delete` transaction with the deleted record’s UUID.
- Delete-reason rules are enforced when required.
- Logging is enforced centrally and cannot be bypassed by modules.
- Logging failures prevent the underlying operation (v1 fail-closed).
- Admins can query sessions and transactions efficiently.

---

## Build Assumptions & Locked Decisions & Locked Decisions

- Naming: This Core capability is titled **Sessions and Event Logging (System Wide)**.
- A top-level **Sessions** table exists.
- A top-level **User Transactions** table exists.
- V1 logs only `create` and `delete` events.
- Events are written only after successful commit.
- Logs are append-only.
- V1 is fail-closed if logging cannot be written.

---

## Out of Scope (Explicit)

- Update events (may be added later)
- Field-level change history
- Business analytics or KPI logging
- External SIEM integrations
- Real-time alerts
- Failed-login transaction events (failures are captured via Sessions only)

---

## Completion Definition

This component is considered complete when:
- A developer can implement session tracking and create/delete event logging using this document alone.
- All modules automatically generate create/delete events without custom logging code.
- Admins can query and review sessions and events reliably.

