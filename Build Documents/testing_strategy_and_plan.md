# BrixaWares Lite - Testing Strategy & Plan

**Objective**: Verify the reliability, usability, and performance of the newly implemented frontend and administration features.

---

## 1. Functional Testing
**Goal**: Ensure all features work according to the "Platform Core" specifications.

### 1.1 Authentication & Core Shell
- [ ] **Login**: Verify successful login with valid credentials deviates to Dashboard.
- [ ] **Login Failure**: Verify invalid credentials show error message.
- [ ] **Logout**: Verify session is cleared and redirects to Login.
- [ ] **Shell Navigation**: Verify sidebar links navigate correctly.
- [ ] **Admin Link Visibility**: Verify "Admin Area" link ONLY appears for Staff/Superusers.

### 1.2 Administration Area
- [ ] **User Management**:
    - [ ] List View: Verify all users follow correct sorting/filtering.
    - [ ] Edit User: Verify toggling "Active" status persists.
- [ ] **Preferences**:
    - [ ] Edit Preference: Verify changing a value (e.g., Retention Count) persists.
    - [ ] Input Validation: Verify invalid types (if implemented) or empty values are handled.
- [ ] **Backup & Restore**:
    - [ ] **Manual Backup**: Trigger backup, wait for completion, verify Success status in table.
    - [ ] **Backup Artifacts**: Verify physical creation of folder and ZIP/JSON files options.
    - [ ] **Settings Display**: Verify dashboard reflects current global settings.
- [ ] **Audit Logs**:
    - [ ] Verify Login/Logout events appear in logs.
    - [ ] Verify User Edit events (`UserTransaction`) appear after modifying a user.

---

## 2. User Acceptance Testing (UAT)
**Goal**: Verify the system is intuitive and meets user expectations ("Look & Feel").

### 2.1 Usability Scenarios
- **Scenario A: The First Login**
    - User logs in -> Sees Welcome message on Dashboard -> Navigates to Admin Area.
    - *Success Criteria*: User feels oriented; navigation is obvious.
- **Scenario B: Emergency Backup**
    - Admin navigates to Backup -> Clicks "Run Manual Backup" -> Sees "Success".
    - *Success Criteria*: Process is transparent; feedback (loading/success) is clear.
- **Scenario C: User Lockout**
    - Admin navigates to Users -> Finds User -> Deactivates them.
    - *Success Criteria*: Action is quick ( < 3 clicks).

### 2.2 Visual Q/A
- [ ] **Responsiveness**: Check layout on different window sizes (Desktop vs Tablet).
- [ ] **Theming**: Verify Brand Colors (Primary Blue) are consistent.
- [ ] **Feedback**: Verify Success/Error messages (Toasts or Alerts) are visible.

---

## 3. Performance Testing
**Goal**: Ensure system responds quickly under expected load.

### 3.1 Page Load Performance
- **Target**: All pages load in < 500ms (Time to First Byte).
- **Test Set**:
    - Dashboard
    - User List (with 50+ users)
    - Audit Log (with 1000+ entries)

### 3.2 Backup Performance
- **Test**: Run Manual Backup with a simulated 100MB database + 500MB file storage.
- **Metrics**:
    - Execution Time: Record seconds to complete.
    - UI Responsiveness: Ensure UI doesn't time out during execution (async check).

### 3.3 Concurrency (Lite)
- **Test**: 2 Admin users accessing Audit Logs simultaneously.
- **Verify**: No database locks or visual artifacts.

---

## 4. Execution Plan (Next Steps)

1.  **Setup Test Data**: Create script to generate dummy users, logs, and files for testing.
2.  **Execute Functional Tests**: Run through checklist manually.
3.  **Execute Performance Tests**: Use `locust` or simple scripts to measure timing.
4.  **Report**: Document bugs/issues found in `test_results.md`.
