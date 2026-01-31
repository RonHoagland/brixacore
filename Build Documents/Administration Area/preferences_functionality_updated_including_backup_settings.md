# Backup & Restore Architecture — On‑Prem (Windows First)

## Purpose
Define a **simple, reliable, non‑technical‑user‑safe** backup and restore strategy for an on‑premise BrixaWares installation.

This document is **authoritative** for backup and restore behavior.

---

## Core Principles
- Backups are **automatic** and **on by default**
- Restore must be possible by a **non‑technical user**
- Backups must survive:
  - application updates
  - crashes
  - partial corruption
- No cloud dependency
- Prefer predictable, low‑complexity behavior over advanced features

---

## Backup Scope by Edition (Locked)

### Lite Edition
- **Database only** (PostgreSQL)
- No documents, attachments, or generated files are backed up

### Pro Edition
- Backup scope is selectable by Admin:
  - **Database only**
  - **Database + Documents**

---

## Backup Locations

### Default Location (Windows)
- `C:\ProgramData\BrixaWares\Backups\`

### User‑Configurable Backup Path
- Backup path is stored in **Backup Settings** (Backup App)
- Must be an absolute path
- **Must NOT be inside the application install directory**
- May point to any drive or mount (e.g., `D:\`, removable, network)

### Enforcement Rules
- Installer sets the default path
- Application validates on save:
  - path exists or can be created
  - path is writeable by the application service
  - path is not a subfolder of the install directory
- No restrictions on drive type; availability is the user’s responsibility

---

## Backup Schedule (Backup App)

### Backup Time
- Stored in **Backup Settings**
- Local system time
- Default: **02:00 AM**
- 24‑hour format
- **Minutes limited to `:00` or `:30` only**

### Frequency
- Daily backups only (v1)

---

## Backup Retention (Backup App)

### Retention Count
- Stored in **Backup Settings**
- Minimum value: **5**
- No upper hard limit

### Enforcement
- Values below 5 are rejected
- After each successful backup:
  - backups sorted oldest → newest
  - oldest backups beyond retention count are deleted

---

## Backup Execution Rules (Locked)

### Automatic Backups
- Only **one automatic backup** may run per day
- If a scheduled backup is missed (machine off / service down):
  - it runs at the **next scheduled interval**

### Manual Backups
- Admins may run manual backups at any time
- Manual backups:
  - do **not** affect the automatic‑backup limit
  - **do count** toward retention

### Concurrency Guard
- Only **one backup may run at a time**
- If a backup is already running (automatic or manual):
  - additional attempts are rejected
  - user sees: “Backup is currently running. Please wait until it finishes.”

### User Freezing
- When a backup starts:
  - logged‑in users are warned
  - all users are **frozen** (read‑only) for the duration
- Normal activity resumes automatically after completion

---

## Backup Format

### Database Backup
- PostgreSQL logical dump
- Single compressed file
- Must restore cleanly to an empty database

### Document Backup (Pro Only)
- Directory snapshot of uploaded and generated documents
- Included **only** when Pro edition is active and scope is set to *Database + Documents*

### Backup Bundle
- Each backup stored as a **single folder** containing:
  - database dump
  - optional document archive (Pro only)
  - metadata file

---

## Backup Metadata
Each backup includes metadata recording:
- backup date/time (UTC)
- backup type (Automatic / Manual)
- backup scope (DB only / DB + Documents)
- app version
- schema version
- database version
- install mode (Solo / Multi‑user)
- backup result (Success / Failed)

---

## Restore Behavior (Non‑Negotiable)

### Restore Scope
- Restore always matches the backup’s scope:
  - DB‑only backup → restores database only
  - DB + Documents backup → restores database and documents

### Restore Process
- Restore is initiated from within the application (Admin only)
- User selects a backup by date/time
- Clear warning shown:
  > “Restoring will overwrite current data. This cannot be undone.”
- On confirmation:
  - application services stop
  - data is restored
  - services restart

### Failure Handling
- If restore fails:
  - system returns to pre‑restore state
  - user is notified clearly

---

## Backup Failure Visibility (Locked)

### Main Entry Screen Notice
- If the most recent scheduled backup fails:
  - show persistent notice on the main entry screen
  - include failure reason and last attempt time

### Example Failure Reasons
- Backup path not available
- Permission denied
- Disk full
- Database dump error

---

## Verification Policy
- Backups are **trusted**
- No automated integrity or test‑restore verification in v1

---

## Upgrade Interaction
- A **mandatory backup** is taken automatically before:
  - application upgrades
  - schema migrations
- Upgrade proceeds only after a successful backup

---

## Non‑Goals
- No cloud sync
- No third‑party backup services
- No incremental or differential backups

---

## Status
Updated — edition‑aware, preferences‑driven, operationally locked

