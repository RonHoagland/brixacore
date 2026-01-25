# BrixaWares Lite - Detailed Implementation Plan

**Objective**: transform the existing backend-ready "Platform Core" into a functional, user-facing desktop application (via browser).

> **Current Status**: Backend is Complete (Schema, Models, Admin, Tests). Frontend is non-existent.

---

## Phase 1: Frontend Infrastructure & Design System

**Goal**: Establish the visual foundation and "App Shell" layout.

- [ ] **Setup Static Files & Assets**
    - [ ] Create `static/css`, `static/js`, `static/img` directories.
    - [ ] Initialize `styles.css` with CSS variables for the color palette (BrixaWares branding).
    - [ ] **Constraint**: All CSS must be in external `.css` files. No inline styles.
    - [ ] **Constraint**: Use CSS Custom Properties (variables) for all colors/fonts to enable easy theming.
- [ ] **Base Templates**
    - [ ] Create `templates/base.html` (HTMX-ready, distinct `<head>`, `<body>`).
    - [ ] Create `templates/includes/` for reusable partials.
- [ ] **App Shell Layout**
    - [ ] Implement `templates/layouts/app_shell.html`.
    - [ ] **Sidebar/Header**: 
        - [ ] Simple navigation (Logout).
        - [ ] **Admin Link**: Only visible if user `is_staff` or `is_superuser`.
        - [ ] **No Modules**: Do not list Sales, Service, etc. in the menu yet.
    - [ ] **Main Content Area**: Container for page content.
- [ ] **HTMX Integration**
    - [ ] Verify `hx-headers` for CSRF protection in `base.html`.
    - [ ] Create generic modal/dialog container for "Quick Create" actions.

## Phase 2: Core UI & Dashboard

**Goal**: functional login/logout and landing page.

- [ ] **Authentication Views**
    - [ ] Login page (`registration/login.html`).
    - [ ] Logout redirection.
    - [ ] Password reset flow (optional for local, but good practice).
- [ ] **Dashboard (Home)**
    - [ ] Create `dashboard` view in `core` or `app_shell` app.
    - [ ] **Placeholders**: Add placeholder cards for future widgets (Welcome, Recent Items, Quick Actions).
    - [ ] **Admin Link**: Ensure obvious link to Django Admin for authorized users.
    - [ ] **Warning Notice**: Persistent banner if backup failed.

## Phase 3: Administration Area

**Goal**: Core platform management.

- [ ] **Preferences UI**:
    - [ ] Form to manage `SystemPreference` model.
    - [ ] **Backup Settings**: Path, Time (HH:00/30), Retention Count.
- [ ] **Backup & Restore UI**:
    - [ ] **Backup History**: List view of available backups (from filesystem).
    - [ ] **Manual Backup**: "Run Backup Now" button (triggers management command).
    - [ ] **Restore**: Modal with "Restoring will overwrite data" warning.
- [ ] **User Management**:
    - [ ] Simple view to list users.
    - [ ] **User Detail/Edit**: View to edit user details (Roles, Active Status, etc.).
- [ ] **Audit Log Viewer**:
    - [ ] List view of `AuditLog` entries with filtering (User, Date, Action).
- [ ] **Admin Home**: Landing page for these tools.

## Phase 4: Polish & "Lite" Restrictions

**Goal**: Ensure the app feels premium but constrained as defined.

- [ ] **UI Polish**
    - [ ] Add loading states (HTMX indicators).
    - [ ] Toast notifications for success/error messages.
    - [ ] Empty states for lists (e.g., "No Clients found. Create one?").
- [ ] **Feature Flags/Licensing UI**
    - [ ] Hide modules based on "Entitlements" (even if just mock boolean flags for now).
- [ ] **Verification**
    - [ ] Verify "Lite" max limits (2 phones, etc) in the UI feedback.
