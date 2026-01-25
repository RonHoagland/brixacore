# Platform Core - Numbering and Identity Services Specification

## Purpose

The **Numbering and Identity Services** component defines how human‑readable identifiers are generated, managed, and enforced across all applications and modules built on the Platform Core.

This service exists to:
- Provide consistent, predictable identifiers for users
- Avoid duplicate or conflicting numbers
- Decouple internal identity (UUIDs) from external-facing identifiers
- Allow modules to opt in to numbering without custom logic

This document defines **what must be built** and **how it must behave**, without prescribing implementation code.

---

## Scope

This document covers:
- Human‑readable numbering schemes
- Number sequence generation and enforcement
- Configuration of numbering rules
- Concurrency and collision prevention
- Administrative control of numbering

This document does **not** cover:
- Primary key generation (UUIDs are defined in Metadata Standards)
- Business logic that depends on number meaning
- External regulatory numbering requirements (handled by modules)

---

## Core Principles

1. **UUIDs Are Canonical**  
   Human‑readable numbers never replace UUIDs as primary keys.

2. **Centralized Control**  
   All numbering is generated through a single Core service.

3. **Deterministic and Predictable**  
   Given the same configuration, numbering behaves consistently.

4. **Collision-Free**  
   Duplicate numbers must never be generated.

5. **Module-Opt‑In**  
   Modules choose whether numbering is required for an entity.

---

## 1) Identity Model

### Internal Identity
- Every record is internally identified by a UUID primary key (`id`).
- UUIDs are system-generated and never exposed as user-facing identifiers by default.

### External / Human‑Readable Identity
- A **Number** is a human‑readable identifier used for display, reference, or communication.
- Numbers are optional per entity and module-defined.

---

## 2) Numbering Definition

### Numbering Rule

A **Numbering Rule** defines how numbers are generated for a specific entity type.

Each rule must define:

- Entity type (e.g., Invoice, WorkOrder, Client)
- Enabled / disabled flag
- Prefix (static text)
- Optional date components (year, month)
- Sequence length and padding
- Reset behavior (none, yearly, monthly)

---

## 3) Number Format

### Supported Components

The numbering service must support combining the following components in order:

1. Optional prefix (e.g., INV, WO)
2. Optional year (YYYY)
3. Optional month (MM)
4. Numeric sequence

### Examples (Conceptual)

- `INV-2026-000123`
- `WO-2026-05-0012`
- `CLIENT-000045`

Format delimiters (e.g., dashes) are configurable.

---

## 4) Sequence Generation

### Sequence Rules

- Sequences must be generated atomically.
- A sequence value may only be used once per rule.
- Sequence generation must be safe under concurrent requests.

### Reset Behavior

If reset is enabled:
- Yearly reset resets the sequence at the start of a new year.
- Monthly reset resets the sequence at the start of a new month.

Reset occurs automatically based on system date.

---

## 5) Assignment Timing

### When Numbers Are Assigned

- Numbers are assigned **once**, at the moment defined by the module.
- Common assignment points include:
  - On record creation
  - On first transition out of a Draft state

The Core must allow the module to specify **when** assignment occurs.

### Immutability

- Once assigned, a number **must never change**.
- Numbers are not reusable, even if a record is deleted.

---

## 6) Configuration & Administration

### Administrative Control

Administrators must be able to:

- Enable or disable numbering per entity
- Configure prefixes, formats, and reset behavior
- View the current sequence value

### Restrictions

- Editing numbering rules must be permission-controlled.
- Changing a rule must not retroactively affect existing numbers.

---

## 7) Validation & Enforcement

### Required Behavior

- If numbering is enabled for an entity, the system must prevent saving a record without a valid number once assignment conditions are met.
- Manual editing of generated numbers is prohibited.

### Error Handling

- If a number cannot be generated, the operation must fail with a clear error.
- Partial saves without a number are not permitted once assignment is triggered.

---

## 8) Auditing

The system must record audit/event entries for:

- Number assignment
- Numbering rule changes

Audit entries must include:
- Timestamp
- User
- Entity type and record id
- Assigned number or rule change details

---

## 9) Module Integration Contract

A module that uses numbering must define:

- Which entities require numbering
- Which numbering rule applies
- When assignment occurs

The Core guarantees:
- Unique, collision-free number generation
- Deterministic formatting
- No duplication across concurrent requests

---

## Acceptance Criteria (Numbering & Identity)

- UUIDs remain the primary key for all entities.
- Numbers are unique within their entity scope.
- Numbers are assigned once and never change.
- Concurrent requests never generate duplicate numbers.
- Numbering rules can be modified without affecting existing records.
- All number assignments and rule changes are auditable.

---

## Build Assumptions & Locked Decisions

- UUID is the sole primary key.
- Numbers are human-facing only.
- Numbers are immutable once assigned.
- Numbers are never reused.
- Sequence generation is centralized and atomic.
- **Uniqueness is guaranteed by the numbering rule itself (prefix/date/sequence), not by cross-entity constraints.**
- **Manual override or manual entry of generated numbers is never allowed.**

---

## Out of Scope (Explicit)

- External regulatory numbering constraints
- Semantic meaning encoded in numbers
- Cross-entity numbering dependencies

---

## Completion Definition

The Numbering and Identity Services component is considered complete when:

- A developer can implement number generation, configuration, and enforcement using this document alone.
- Modules can adopt numbering without custom generation logic.
- All identifiers are predictable, collision-free, and auditable.

