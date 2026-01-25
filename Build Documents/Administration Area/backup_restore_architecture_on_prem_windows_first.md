# Backup & Restore Architecture — On‑Prem (Windows First)

## Purpose
Define a **simple, reliable, non‑technical‑user‑safe** backup and restore strategy for an on‑premise BrixaWares installation.

This document is **authoritative** for backup and restore behavior.

---

## Core Principles
- Backups are **automatic** and **on by default**
- No user configuration required for baseline safety
- Restore must be possible by a **non‑technical user**
- Backups must survive:
  - application updates
  - crashes
  - partial corruption
- No cloud dependency

---

## What Must Be Backed Up (Locked)

### Data Components
- PostgreSQL database (entire cluster or dedicated DB)
- Uploaded documents / attachments
- Generated documents (PDFs, exports)
- Application configuration files (mode, ports, paths)

### Explicitly NOT Backed Up
- Application binaries
- Installer files
- OS‑level components

---

## Backup Locations

### Default Location (Windows)
- `C:\ProgramData\BrixaWares\Backups\`

### User-Configurable Backup Path (Preferences)
- Backup path is stored in **Preferences**
- Must be an absolute path
- **Must NOT be inside the application install directory**
- May point to:
  - another local drive (e.g., `D:\BrixaWares_Backups\`)
  - a mounted internal disk

### Enforcement Rules
- Installer sets a safe default path
- Application validates on save:
  - path exists or can be created
  - path is writeable by the service account
  - path is not a subfolder of the install directory
- No restrictions on drive type (internal, secondary, removable, or network-mounted). Responsibility for availability rests with the user.

---

## Backup Schedule (Preferences-Driven)

### Backup Time
- Backup run time is stored in **Preferences**
- Time is local system time
- Default: **02:00 AM**
- Validated input (HH:MM, 24-hour)

### Backup Frequency
- Daily backups only (v1)

---

## Backup Retention (Preferences-Driven)

### Retention Count
- Total number of backups to keep is stored in **Preferences**
- Minimum allowed value: **5**
- No upper hard limit enforced

### Enforcement Rules
- Values below 5 are rejected
- On successful backup completion:
  - backups are sorted oldest → newest
  - oldest backups beyond retention count are deleted

---

## Backup Format

### Database Backup
- PostgreSQL logical dump
- Single compressed file per backup
- Must be restorable to an empty database without manual steps

### File Backup
- Directory snapshot of:
  - uploads
  - generated documents
- Stored alongside DB dump

### Backup Bundle
- Each backup stored as a **single folder** containing:
  - DB dump
  - file archive
  - metadata file

---

## Backup Metadata
Each backup includes a metadata file containing:
- backup timestamp (UTC)
- app version
- schema version
- database version
- install mode (Solo / Multi-user)

---

## Restore Requirements (Non‑Negotiable)

### Restore Capabilities
- Restore from **any retained backup**
- Restore must:
  - stop application services
  - restore database
  - restore files
  - restart services

### Restore UX
- Restore initiated from within the application
- User selects backup by **date/time**
- Clear warning displayed:
  > “Restoring will overwrite current data. This cannot be undone.”

### Failure Handling
- If restore fails:
  - system must return to pre‑restore state
  - user must be notified clearly

---

## Upgrade Interaction
- **Mandatory backup** taken automatically before:
  - application upgrades
  - schema migrations
- Upgrade proceeds only after backup succeeds

---

## Non‑Goals
- No cloud sync
- No third‑party backup services
- No incremental/differential backups in v1

---

## Backup Execution Behavior (Operational Rules)

### Concurrency & User Freezing (Locked)
- When a scheduled or manual backup begins:
  - If any users are currently logged in, the system must:
    - display a warning to those users that a backup is starting
    - **freeze all users** (read-only / no writes) for the duration of the backup
- After backup completion (success or failure):
  - normal user activity resumes automatically

### Manual Backup
- An **Admin** can run a backup from the **Admin section** ("Run Backup Now")

---

## Backup Failure Visibility (Locked)

### Main Entry Screen Notice
- If the most recent scheduled backup fails, show a persistent notice on the **main entry screen** that includes:
  - backups have failed
  - the reason (human-readable)
  - the date/time of the last attempted backup

### Failure Reasons (examples)
- Backup path not available
- Insufficient permissions to write to backup path
- Disk full
- Database dump error

---

## Backup Verification
- The system **trusts the dump**.
- No automated test-restore or integrity verification in v1.

---

## Status
Draft — initial baseline

