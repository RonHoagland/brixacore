# Platform Core - Status and Lifecycle Framework Specification

## Purpose

The **Status and Lifecycle Framework** defines the universal mechanism used to represent, validate, and enforce record state across all applications and modules built on the Platform Core.

This framework provides:

- A consistent way to store “where a record is in its lifecycle”
- Rules for valid state transitions
- Locked/final states
- Standard audit/event logging of state changes
- A predictable integration contract for modules

This document defines **what must be built** and **how it must behave**, without prescribing implementation code.

---

## Scope

This document covers:

- Lifecycle state representation
- Transition rule definition and enforcement
- Locked/final states
- Transition auditing/event logging
- Permissions interaction for state changes
- Module integration contract

This document does **not** cover:

- Business-specific state sets (each module defines its own)
- Non-state business validation rules
- UI layout requirements (covered by Application Shell)

---

## Core Principles

1. **Framework, Not Business Logic**\
   Core provides the mechanism. Modules define their states.

2. **Explicit Transitions**\
   States do not “just change.” Transitions must be declared and validated.

3. **Fail Closed**\
   If a transition is not explicitly allowed, it is denied.

4. **Auditable State Changes**\
   Every state change must be traceable.

5. **Predictable Integration**\
   Every module uses the same lifecycle contract.

---

## 1) Lifecycle Concepts

### Lifecycle vs Operational Flags

- **Lifecycle State** represents workflow progression (e.g., Draft → Approved → Closed).
- **Operational flags** (e.g., `is_active`) are not lifecycle and are handled separately.

### Terminology

- **State**: A named value indicating the record’s lifecycle position.
- **Transition**: A change from one state to another.
- **Locked State**: A state that restricts or prevents certain changes.
- **Final State**: A state that has no outgoing transitions.

---

## 2) Lifecycle State Representation

### Required Fields (Per Lifecycle-Enabled Entity)

Any entity that uses lifecycle must include:

- **lifecycle\_state** (string/enum)

Optional but supported:

- **lifecycle\_reason** (string) – when a transition requires justification
- **lifecycle\_changed\_at** (datetime) – last time lifecycle\_state changed
- **lifecycle\_changed\_by** (UUID) – who last changed lifecycle\_state

### Default State

- Every lifecycle-enabled entity must define a default initial state.
- The default state is applied at record creation.

---

## 3) State Definitions (Module-Owned)

Modules must define, for each lifecycle-enabled entity:

- List of allowed states
- Default initial state
- Whether each state is:
  - Normal
  - Locked
  - Final
- Human-friendly display labels (optional but recommended)

Core must provide a place/mechanism to register these definitions.

---

## 4) Transition Rules

### Transition Definition

A transition rule must specify:

- Entity type
- From-state
- To-state
- Optional permission requirement
- Optional requirement for a reason (text)

### Enforcement Rules

- Transitions must be validated server-side.
- If a transition is not defined, it is denied.
- Transitions must not be performed by direct field updates that bypass validation.

### Self-Transitions

- Self-transitions (A → A) are not permitted unless explicitly allowed.

---

## 5) Locked and Final State Rules

### Locked State (Core Meaning)

A locked state is a state in which the record becomes restricted.

Core must support module-defined restrictions, including:

- Block edits to the record
- Block deletes of the record
- Allow only specific fields to change (optional; see note below)

**Core baseline:** field-level restriction is not required at the Core level. If field-level locking is needed later, it must be introduced via a separate, explicitly approved standard.

**Locked State Rule:**

> When a record is in a locked or final state, **no edits are allowed**.

> All modification actions are blocked regardless of permission level, except for allowed lifecycle transitions (including admin overrides).

### Final State

A final state:

- Has no outgoing transitions
- Is treated as locked unless a module explicitly states otherwise

---

## 6) Permissions Interaction

### State Change Permissions

- A lifecycle transition may require a permission.
- If a permission is required, the transition must be denied without it.

### Default Behavior

- If a transition rule does not specify a permission, it inherits the entity’s general edit permission.

### Administrative Override

Administrators may perform **explicit lifecycle override transitions**.

Override rules:
- Requires a dedicated administrative permission
- Must be executed through the lifecycle framework (no direct field updates)
- May bypass normal transition rules, including final-state restrictions
- Must require an override reason
- Must generate a distinct audit/event entry clearly marked as an override

---

## 7) Transition Auditing / Event Logging / Event Logging

Every successful transition must generate an audit/event entry containing:

- Timestamp
- User who performed the transition
- Entity type and entity id (UUID)
- From-state
- To-state
- Reason text (if required and provided)

Audit entries must be immutable.

---

## 8) Error Handling

### Invalid Transitions

When a transition is denied, the system must return:

- Clear error message identifying the attempted transition
- Reason for denial (not allowed / missing permission / missing reason)

### Missing State Definitions

If a lifecycle-enabled entity has no registered state definitions:

- The system must fail closed and block lifecycle operations for that entity.

---

## 9) Module Integration Contract

A module that uses lifecycle must register:

- Entity type
- Allowed states
- Default state
- Transition rules
- Locked/final flags per state

The Core must guarantee:

- Uniform enforcement
- Deterministic allow/deny
- Audit/event generation for every transition

---



## Acceptance Criteria (Lifecycle Framework)

- A lifecycle-enabled entity cannot enter a state outside its registered state set.
- A record cannot transition unless an explicit transition rule allows it.
- Transition rules are enforced server-side.
- Locked/final state behavior is enforced.
- Every successful state change generates an audit/event entry.
- Modules can register lifecycle definitions without modifying the Core framework.

---

## Build Assumptions & Locked Decisions

- Lifecycle is opt-in per entity.
- State values are treated as enumerations (only allowed values may be stored).
- Deny-by-default for transitions.
- Direct field writes that bypass the transition mechanism are prohibited.
- Locked and final states allow **no edits**.
- Administrative override transitions are allowed only with explicit permission and mandatory auditing.

---

## Out of Scope (Explicit)

- Field-level security
- Row-level security
- Automatic state changes driven by business events (module responsibility)
- Workflow timers/escalations (module responsibility)

---

## Completion Definition

The Status and Lifecycle Framework is considered complete when:

- A developer can implement lifecycle storage, registration, validation, and auditing using this document alone.
- Modules can define states and transitions without custom logic outside the framework.
- State changes are consistent, enforceable, and auditable across all modules.

