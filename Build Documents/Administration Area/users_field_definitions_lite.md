# Users – Field Definitions (Lite)

> **Product:** BrixaWares  \
> **Database targets:** SQLite (dev) → MySQL (prod)  \
> **Status:** Draft  \
> **Scope:** Field dictionary for the **Users** table only (no code).  \
> **Note:** User authentication and session management are handled separately.

---

## 1) Table: `users`

### Purpose
Stores the core identity and access context for system users. Users represent internal actors who can log in and perform work within BrixaWares.

### Housekeeping Fields (always present)
All tables include these fields:
- `id` (UUID, CHAR(36)) – unique across the whole data structure
- `created_by` (CHAR(36)) – the logged-in user (UUID) that created the record
- `created_on` (DATETIME/TIMESTAMP) – server timestamp at creation (not user-controlled)
- `modified_by` (CHAR(36)) – the last user (UUID) to modify the record
- `modified_on` (DATETIME/TIMESTAMP) – server timestamp at last modification (not user-controlled)

---

## 2) Field Dictionary

> **Type conventions**
> - SQLite types are shown as practical affinities.
> - MySQL types assume InnoDB and UTF-8 (utf8mb4).

| Field Name | Type (SQLite) | Type (MySQL) | Required | Default | What it does | Rules / Functionality |
|---|---|---|---:|---|---|---|
| `id` | TEXT | CHAR(36) | Yes | system-generated | Primary key UUID | Immutable. Unique across system. |
| `employee_number` | TEXT | VARCHAR(10) | Yes | system-generated | Human-readable employee number | Format: `EMP<YY><NN>`. Two-digit year (server local time) + 2-digit serial, zero-padded. Unique within Users. Assigned on create. Not user-editable. |
| `username` | TEXT | VARCHAR(50) | Yes | — | Login identifier | Case-insensitive. Alphanumeric + underscore/hyphen allowed. Min 5 chars, max 20. Uniqueness not required (employee_number is the unique user handle). |
| `email` | TEXT | VARCHAR(150) | Yes | — | Email address | Must be unique within Users. Used for password reset and communication. Standard email validation. |
| `first_name` | TEXT | VARCHAR(25) | Yes | — | User first name | Required. Used in UI display and audit logs. |
| `last_name` | TEXT | VARCHAR(50) | Yes | — | User last name | Required. Used in UI display and audit logs. |
| `password_hash` | TEXT | VARCHAR(255) | Yes | — | Hashed password | Never stored as plain text. Uses bcrypt or equivalent. Updated on password change only. |
| `password_salt` | TEXT | VARCHAR(255) | Yes | — | Password salt | Used in conjunction with password_hash. Generated on user creation and password reset. |
| `password_changed_on` | TEXT | TIMESTAMP | No | NULL | Last password change timestamp | Server-generated. Updated when password is reset. NULL until first password change after creation. |
| `status` | TEXT | VARCHAR(25) | Yes | Active | User lifecycle status | Value List: Active, On Leave, Inactive, Terminated. Determines login ability and visibility in pickers. Only Active users can log in. |
| `is_owner` | INTEGER | BOOLEAN | Yes | 0 (false) | Owner/Admin flag | Lite only: First user created is automatically set to true. Cannot be changed via UI in Lite. Indicates Owner/Admin role. |
| `is_system_user` | INTEGER | BOOLEAN | Yes | 0 (false) | System user flag | Reserved for future use. Identifies automated/integration users (Pro feature). |
| `created_by` | TEXT | CHAR(36) | Yes | system user | Creator user UUID | Set from authenticated session/user context. |
| `created_on` | TEXT | TIMESTAMP | Yes | server timestamp | Created timestamp | Must be server-generated. User cannot influence. |
| `modified_by` | TEXT | CHAR(36) | Yes | system user | Last modifier user UUID | Updated on every change. |
| `modified_on` | TEXT | TIMESTAMP | Yes | server timestamp | Last modified timestamp | Must be server-generated. Updated on every change. |

---

## 3) Related Entities (Not defined here)

The following are **separate tables/entities**. This document only defines the `users` table, but Users relate to these other tables.

### 3.1 User Roles (separate table: `user_roles`)
- Represents the assignment of a Role to a User
- Links `users.id` to `roles.id`
- Effective date and expiration date for role assignments (Pro feature)
- Stored for audit and historical tracking

### 3.2 Roles (separate table: `roles`)
- Defined in **roles_field_definitions_lite.md**
- In Lite: three predefined roles (Owner/Admin, Worker/User, Read-Only)
- Custom roles are a Pro feature

### 3.3 Value Lists (separate table: `value_lists`)
- Stores the enumerated values for dropdowns and status fields
- Includes: User Lifecycle Status values
- Defined in **value_lists_field_definitions_lite.md**

---

## 4) Lite-Specific Rules

### 4.1 User Creation (Lite)

- **First user** created is automatically set as:
  - `is_owner = true` (Owner/Admin role)
  - `lifecycle_status = Active`

- **Subsequent users** are created by the Owner with:
  - `is_owner = false`
  - `lifecycle_status = Active` (default)
  - Default role assigned (Worker/User or Read-Only)

### 4.2 User Editing (Lite)

- Users may edit their **own password and email**
- Owner may edit **any user's email, name, lifecycle_status, and role assignment**
- Owner cannot edit their own `is_owner` flag
- Username is **immutable** after creation

### 4.3 User Deletion (Lite)

- Users are **not deleted**; lifecycle_status is set to **Inactive** or **Terminated**
- Historical audit and data creation/modification records persist
- Inactive users:
  - Cannot log in
  - Do not appear in most pickers
  - Are visible in User Admin list

### 4.4 Uniqueness Constraints

- `employee_number` is unique within Users
- `email` is unique within Users
- `username` is allowed to duplicate; disambiguation in UI/pickers uses `employee_number` + name

---

## 5) Lite vs Pro Differences

### Lite
- Three predefined roles only (Owner/Admin, Worker/User, Read-Only)
- No custom role creation
- No role expiration dates
- No IP restrictions

**Notes (Lite auth/identity)**
- `employee_number` is the canonical human-readable identifier for Users; it is unique and system-generated. Usernames may duplicate.
- Implementation will use the built-in Django User system; employee_number is stored alongside it as the business identifier.
- Django’s default User enforces unique `username`; for this build, we will either relax that constraint (custom user model) or treat `employee_number` as the true handle and allow duplicate usernames, with UI/pickers always showing `employee_number` + name for clarity.

### Pro (Future)
- Additional predefined roles (Manager, Accountant, etc.)
- Custom role creation
- Role assignment with effective/expiration dates

---

## 6) Default Values Summary

| Field | Lite Default |
|---|---|
| `lifecycle_status` | Active |
| `is_owner` | false (true only for first user) |
| `is_system_user` | false |
| `employee_number` | system-generated on create |
| `created_on` | current server timestamp |
| `modified_on` | current server timestamp |

---

## 7) Validation Rules

- `username`: 
  - Min 5 characters, max 20
  - Alphanumeric, underscore, hyphen only
  - Case-insensitive
  - May duplicate; UI disambiguates by showing `employee_number` + name
  
- `email`: 
  - Valid email format
  - Unique within Users
  
- `first_name` / `last_name`: 
  - Non-empty strings
  - Max 25 and 50 characters respectively
  
- `password_hash`: 
  - Must be present and non-empty
  - Bcrypt hash (minimum 60 characters)

- `employee_number`:
  - Format `EMP<YY><NN>`
  - YY = last two digits of server local time year
  - NN = 2-digit serial per year, zero-padded
  - Assigned on create; not editable

---

> **Next step:** Create corresponding **Users – Lite Functionality** document defining user management UI/UX behavior.
