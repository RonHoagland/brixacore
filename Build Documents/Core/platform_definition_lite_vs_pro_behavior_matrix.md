# Platform Definition - Lite vs Pro Behavior Matrix

## Purpose

This document defines **system-wide behavior differences** between **Lite** and **Pro** editions while sharing the same **Platform Core**.

The Platform Core is identical across editions. Differences are implemented through:
- Feature flags / licensing rules
- Module enablement
- UI visibility rules
- Export capabilities

This document is intentionally **system-wide** and avoids module-specific business details.

---

## Core Rules (Apply to Lite and Pro)

These behaviors do **not** change by edition:

- **No editing from list views** (lists are view + create only)
- Editing and deleting occur in **Detail View** only
- UUIDs are primary keys for all records
- Hard delete is standard; default delete rule is **restrict if dependent children exist**
- Lifecycle transitions are enforced by the Lifecycle Framework; locked/final states allow **no edits**
- Admin override transitions are allowed with explicit permission + audit
- Sessions and event logging:
  - Session record created on every login attempt (success/failure)
  - Create/Delete user transactions are logged system-wide
- Background jobs framework exists (v1 primarily backup job)

---

## Edition Differences Summary

### Lite Edition Philosophy
- Lowest development/maintenance cost
- List views + filters are the reporting strategy
- Minimal automation and operational complexity
- No bulk operations

### Pro Edition Philosophy
- Adds power-user operational features
- Adds more exports and advanced admin controls
- Enables additional modules (e.g., Procurement/Vendors)

---

## 1) Module Availability

### Lite
- Core modules only (as defined in module specs)
- **No procurement** functionality
- **No Vendors** module (branch/pro feature)

### Pro
- Core modules + optional advanced modules
- Procurement/Vendors eligible for enablement

---

## 2) List Views and Actions

### Lite
- **No bulk actions anywhere**
- List views provide:
  - Filter, sort, search
  - View Details
  - Create New
  - CSV export (see exports)

### Pro
- **No bulk actions anywhere**
- List views provide the same capabilities as Lite

---

## 3) Exports

### Lite
- Export format: **CSV only**
- Export scope: **List views only**

### Pro
- Export formats:
  - CSV
  - JSON
  - PDF (only if using a free library; otherwise not included)
- Export scope:
  - List views only

---

## 4) Reporting Strategy

### Lite
- Reporting is performed via:
  - List views + saved filters (if supported)
  - Browser print for hard copies
- No advanced reporting engine

### Pro
- Uses the same list-view reporting baseline
- May add advanced reports per module and edition

---

## 5) File Backups (System Wide)

### Lite
- Automatic backup supports: **Database only**

### Pro
- Automatic backup supports:
  - Database only
  - Database + Documents (file storage)

---

## 6) Background Jobs and Automation

### Lite
- Background Jobs framework is present
- Primary scheduled job: **Backup**
- Scheduling constraints:
  - Scheduled on **30-minute increments**
  - Retries: **5 max**, **1-minute delay**

### Pro
- Same scheduler rules
- Additional scheduled jobs may be enabled per module (cleanup, maintenance, etc.)

---

## 7) Administration

### Lite
- Minimal admin surface area
- Admin can:
  - Manage users/roles/permissions
  - Manage preferences/value lists
  - Configure backup path and schedule

### Pro
- Expanded admin controls may include:
  - Additional module management
  - Advanced backup options
  - Maintenance job controls

---

## 8) Licensing and Feature Flags

### Lite
- Feature flags default to Lite-allowed modules and capabilities
- Disallowed features must be:
  - Hidden from navigation
  - Blocked by route and server-side checks

### Pro
- Feature flags enable Pro-allowed modules and capabilities
- Same enforcement rules

---

## Acceptance Criteria (Lite vs Pro)

- The same Platform Core runs both editions.
- Switching editions changes behavior **only** through licensing/feature flags.
- Neither Lite nor Pro support bulk actions.
- Neither Lite nor Pro support saved views or saved filters.
- Lite has:
  - CSV-only exports
  - DB-only backups
  - No procurement/vendors
- Pro adds:
  - Additional export formats (JSON/PDF where available)
  - Optional DB+Documents backups
  - Procurement/vendors eligible

