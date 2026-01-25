# Platform Core - File and Binary Storage Infrastructure Specification

## Purpose

The **File and Binary Storage Infrastructure** defines how files and binary objects are stored, referenced, secured, and managed across all applications built on the Platform Core.

This component provides a **centralized, predictable, and secure mechanism** for handling files without embedding business meaning into the storage layer.

This document defines **what must be built** and **how it must behave**, without prescribing implementation code.

---

## Scope

This document covers:

- Physical storage strategy (paths, organization)
- File metadata management
- File referencing and attachment patterns
- Upload, download, and deletion rules
- Access control and permissions
- Retention and cleanup rules (framework-level)

This document does **not** cover:

- Business rules for when files are required
- Document workflows or approvals
- Versioning of file contents
- External cloud storage integrations

---

## Core Principles

1. **Infrastructure, Not Documents**\
   Core manages files as binary objects. Business meaning is added by modules.

2. **Single Source of Truth**\
   All files are stored and accessed through the Core infrastructure.

3. **Predictable Paths**\
   Storage paths must be deterministic and configurable.

4. **Secure by Default**\
   Direct file access is never allowed without permission checks.

5. **Metadata + Binary Separation**\
   File metadata lives in the database; binary content lives in storage.

---

## 1) Storage Model

### Storage Root

- A single **storage root path** is defined via System Configuration.
- All files are stored under this root.

### Path Structure (Standard)

The Core must store files using a deterministic directory structure:

- `{storage_root}/{entity_type}/{entity_id}/{file_id}`

Where:

- `entity_type` = logical owning entity (e.g., Client, Invoice)
- `entity_id` = UUID of the owning record
- `file_id` = UUID of the file metadata record

This structure:

- Prevents filename collisions
- Keeps files grouped by ownership
- Allows safe cleanup when records are deleted

---

## 2) File Metadata

### File Metadata Record

Every stored file must have a corresponding metadata record.

#### Required Metadata Fields

- `id` (UUID, PK)
- `original_filename`
- `stored_filename` (UUID + sanitized original filename)
- `storage_path`
- `mime_type`
- `file_size`
- `created_at`
- `created_by`

Optional but supported:

- `checksum` (for integrity verification) (Pro Only)1
- `description`

---

## 3) Upload Rules

### Upload Process

- Files are uploaded through Core-controlled endpoints only.
- File metadata record is created before or during binary write.
- Binary write and metadata creation must be treated as a single logical operation.

### Validation

The Core must enforce:

- Maximum file size (configurable via System Preferences)
- Allowed mime types (configurable)

**File Size Limits**
- A hard Core maximum file size of **500 MB** is enforced.
- Users may configure a lower maximum via Preferences.
- Attempts to upload files exceeding either limit must be rejected before storage.

Uploads that fail validation must be rejected before storage.

---

## 4) Download Rules

### Access Control

- File downloads must be permission-checked.
- Access is determined by:
  - User permissions
  - Access to the owning entity

### Delivery

- Files are streamed through the application layer.
- Direct filesystem access by clients is prohibited.

---

## 5) File Deletion Rules

### Delete Triggers

Files may be deleted when:

- Explicitly deleted by a user with permission
- Owning entity is hard-deleted (subject to module rules)

### Delete Behavior

- File metadata record must be deleted.
- Binary file must be removed from storage.
- Deletion must generate a User Transaction event (delete).

### Failure Handling

- Partial deletes (metadata deleted but file remains, or vice versa) must not occur.
- If deletion fails, the operation must fail.

---

## 6) Attachment & Referencing Pattern

### Ownership Model

- A file is owned by exactly **one** entity.
- Files are not shared across entities at the storage level.

### Linking

- Modules may link files to additional entities via linking tables (outside Core scope).
- Physical storage remains tied to the owning entity only.

---

## 7) Retention & Cleanup (Framework-Level)

### Default Behavior

- Files are retained indefinitely by default.

### Cleanup Hooks

- Core must provide hooks for modules to:
  - Identify orphaned files
  - Define cleanup rules

Actual cleanup policies are module- or admin-defined.

---

## 8) Security Requirements

- Stored files must not be web-accessible by path.
- File paths must never be exposed directly to clients.
- Permissions must be re-checked on every download request.

---

## 9) Indexing & Performance

### Database

- Index on `created_at`
- Index on owning `entity_type` + `entity_id`

### Storage

- Directory depth must remain predictable and bounded.
- No single directory should contain excessive file counts.

---

## Acceptance Criteria (File Storage)

- Files are stored under a single configurable root.
- File paths are deterministic and collision-free.
- Metadata and binary content remain consistent.
- Unauthorized users cannot access files.
- File deletes remove both metadata and binary content.
- Storage infrastructure is reusable across all modules.

---

## Build Assumptions & Locked Decisions

- Storage is filesystem-based (local or mounted volume).
- No direct client access to storage paths.
- One owning entity per file.
- Files are immutable after upload (replace = new file).
- Stored filenames use **UUID + sanitized original filename**.
- Maximum file size is configurable via Preferences with a hard Core cap of **500 MB**.

---

## Out of Scope (Explicit)

- File versioning
- Deduplication
- External object storage (S3, etc.)
- Content indexing/search

---

## Completion Definition

The File and Binary Storage Infrastructure is considered complete when:

- A developer can implement file upload, storage, retrieval, and deletion using this document alone.
- Modules can attach files without custom storage logic.
- Files are secure, traceable, and consistently managed across the platform.

