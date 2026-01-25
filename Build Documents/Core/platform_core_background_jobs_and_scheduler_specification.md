# Platform Core - Background Jobs and Scheduler Specification

## Purpose

The **Background Jobs and Scheduler** component defines how asynchronous, deferred, and scheduled work is executed across all applications built on the Platform Core.

This component provides a **reliable, centralized execution framework** for tasks that must not block user interactions, must run on a schedule, or must be retried safely.

This document defines **what must be built** and **how it must behave**, without prescribing implementation code.

---

## Scope

This document covers:
- Background job execution
- Scheduled jobs (time-based)
- Job lifecycle and state management
- Concurrency control and locking
- Failure handling and retries
- Administrative visibility and control

This document does **not** cover:
- Business logic executed by jobs
- External workflow/orchestration engines
- Distributed job execution across multiple nodes (v1)
- Real-time stream processing

---

## Core Principles

1. **Non-Blocking by Design**  
   Jobs run outside of user request/response cycles.

2. **Deterministic Execution**  
   Jobs must not run unpredictably or concurrently unless explicitly allowed.

3. **Fail Safe**  
   Failures must be visible, logged, and recoverable.

4. **Single Authority**  
   The Core scheduler is the only mechanism allowed to run background jobs.

5. **Auditable**  
   Job execution and outcomes must be traceable.

---

## 1) Job Model

### Job Definition

A **Job** represents a unit of background work to be executed by the system.

Each job must define:
- Job type/name
- Payload (job-specific data)
- Execution rules (immediate vs scheduled)
- Retry behavior

---

## 2) Job Types

### Immediate Jobs
- Executed as soon as possible after being queued.
- Used for deferred work triggered by user actions.

### Scheduled Jobs
- Executed based on a schedule.
- Used for recurring or time-based operations (e.g., backups, cleanup).

---

## 3) Job Lifecycle

### Job States

Jobs must transition through the following states:

- **Queued** – waiting to be executed
- **Running** – currently executing
- **Completed** – finished successfully
- **Failed** – execution failed
- **Cancelled** – explicitly cancelled before execution

State transitions must be enforced by the Core.

---

## 4) Job Metadata (Required Fields)

Every job record must include:

- `id` (UUID, PK)
- `job_type`
- `status` (queued, running, completed, failed, cancelled)
- `payload` (JSON/text)
- `scheduled_at` (datetime, nullable)
- `started_at` (datetime, nullable)
- `completed_at` (datetime, nullable)
- `attempt_count`
- `max_attempts`
- `last_error` (text, nullable)
- `created_at`
- `created_by` (UUID or system user)

---

## 5) Scheduling Rules

### Time-Based Scheduling

- Jobs may be scheduled at a specific datetime.
- Scheduler resolution is **minute-level**.
- Recurring schedules must support:
  - Hourly
  - Daily
  - Weekly

**V1 Note:** The primary scheduled job is the Backup job, which runs on **30-minute increments**.

Schedule definitions are configuration-driven.

### Missed Runs

- If a scheduled job is missed (system down, delayed), it must run at the next eligible opportunity.
- Missed runs must not cause duplicate executions.

---

## 6) Concurrency and Locking

### Single-Run Guarantee

- A job may not execute concurrently with itself.
- Locking must be enforced at the Core level.

### Job-Type Concurrency

- Some job types may be restricted to a single active instance at a time.
- Concurrency rules are defined per job type.

---

## 7) Failure Handling and Retries

### Retry Rules

- Automatic retries are **enabled by default**.
- Maximum retry attempts: **5**.
- Retry delay: **1 minute** between attempts.
- Retry counters increment on each failed execution attempt.

### Failure State

- When retries are exhausted, the job enters **Failed** state.
- Failures must record error details in `last_error`.

---

## 8) Administrative Control

Administrators must be able to:
- View all jobs and their statuses
- Filter jobs by type, status, and date
- Manually retry failed jobs
- Cancel queued jobs

Administrative actions must be permission-controlled and auditable.

---

## 9) Integration with Sessions & Event Logging

- Job creation must generate a User Transaction (create) when initiated by a user.
- Job execution events must be logged internally for troubleshooting.
- Jobs triggered by the system use the system user identity.

---

## 10) Indexing & Performance

### Required Indexes

- Index on `status`
- Index on `job_type`
- Index on `scheduled_at`
- Index on `created_at`

---

## Acceptance Criteria (Background Jobs)

- Jobs execute outside user request cycles.
- Scheduled jobs run at correct times without duplication.
- Jobs do not run concurrently unless explicitly allowed.
- Failures are logged and retry behavior is enforced.
- Administrators can manage jobs safely.

---

## Build Assumptions & Locked Decisions

- Jobs are executed within the same application environment (single-node v1).
- Job payloads are opaque to the Core.
- Automatic retries are enabled by default.
- Maximum retries per job: **5**.
- Retry delay is fixed at **1 minute**.
- Scheduler resolution is **minute-level**.
- All job execution flows through this Core framework.

---

## Out of Scope (Explicit)

- Distributed job queues
- External schedulers (cron outside the app)
- Real-time streaming jobs

---

## Completion Definition

The Background Jobs and Scheduler component is considered complete when:

- A developer can implement job queuing, scheduling, execution, and retry handling using this document alone.
- Modules can schedule background work without custom schedulers.
- Job execution is reliable, observable, and controllable.

