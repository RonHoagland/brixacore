# Platform Core - Application Shell Specification

## Purpose

The **Application Shell** is the foundational UI/UX framework that every application and module runs inside. It provides consistent navigation, page structure, common interaction patterns, and a shared contract for how modules register screens, lists, detail views, and actions.

This specification describes **what must be built** (behavior and structure). It intentionally contains **no code**.

---

## Goals

- Provide a consistent, reusable container for all modules and future applications.
- Ensure every module can plug in without custom wiring.
- Standardize list/detail behaviors (filtering, searching, sorting, actions, navigation).
- Support feature-flag-based enable/disable of modules without breaking navigation.
- Keep the shell “dumb” about business logic; it renders whatever modules register.

---

## Non-Goals

- The Application Shell does not define business entities (Clients, Products, etc.).
- The Application Shell does not implement business workflows.
- The Application Shell does not include report definitions (only the mechanics).

---

## Conceptual Model

The Application Shell is composed of five major areas:

1. **App Container** (layout + global chrome)
2. **Navigation System** (menus, shortcuts, breadcrumbs)
3. **Routing & Page Registry** (how pages are registered and opened)
4. **Standard Views** (List View, Detail View, optional Dashboard View)
5. **Action Framework** (standard button/actions behavior and permissions)

---

## 1) App Container (Global Layout)

### Required Layout Regions

- **Top Bar (Header)**

  - List 
  	- Module name In Center (Title) / Large Font
  	- Breadcrumbs
  	- Module search entry point Bottom Right
  	- Main Navigation Menu above Search Bar
  		- Home, User, Show All, Filter List Dropdown, Quick Navigation Dropdown
  - Detail View
  	- Breadcrumbs
  	- Notifications indicator (framework hook; does not require notifications content)
  	- Module Name in Large font to the Top Right

- **Primary Navigation (Left Sidebar or Top Tabs)**

  - List
  	- Top Left under Search Bar.  Top Tabs Button Bar (See top bar for buttons)
  	
  - Details
	- Left sidebar going from top to bottom
		- Home, List View, New Record, Edit, Delete, Operations (Actions to perform specific to the Module).

- **Main Content Area**

  - Page content

- **Footer**

  - List View
  	- Build/version string (Center)
  - Details View
  	- Housekeeping fields (non-editable) (Center)
  	- Full Calendar Date - Thursday, January 8, 2026 (Right)

### Global Behaviors

- Consistent spacing, typography, and component styling.
- Works at common desktop resolutions; responsive behavior required (at minimum: sidebar collapse).
- Does not hardcode business pages; everything is driven by the Page Registry.

---

## 2) Navigation System

### Navigation Types (Must Support)

1. **Main Menu List View**

   - Right horizontal Menu.  Sits above the Search Bar.
   - Home, User, Show All, Filter List Dropdown, Quick Access Dropdown, Module Operations
   	- Module Operations should include New Record and any other operations for the specific module

2. **Contextual Navigation (Within a Module)**

   - Tabs or secondary menu within a module section.
   - Example: a module may register “List”, “Create”, “Settings”.

3. **Breadcrumbs**

   - Auto-generated from route/page metadata.
   - Supports deep navigation (List → Record → Related Tab).

4. **Quick Access**

   - Dropdown of all registed modules. Takes user to list view for given module selected.
   
 5. **Sidebar Menu Details View**
   - Left sidebar on the details view
   - Home, List View, New Record, Edit, Delete, Module Operations (Module Actions to perform).

### Permissions & Visibility

- Menu entries must respect:
  - Role permissions
  - Feature flags/licensing
  - Module enablement

### Requirements

- Navigation must be data-driven and registered, not hardcoded.
- A module can add/remove entries without altering the shell code.

---

## 3) Routing & Page Registry

### Page Registry Responsibilities

The shell must implement a registry that defines:

- **Pages** (screens) available in the system
- **Routes** (URLs / navigation keys) mapped to pages
- **Page metadata** (title, icon, module group, permissions, feature flag requirements)

### Page Types (Minimum)

- **Dashboard Page** (optional per module)
- **List Page** (standard list view)
- **Detail Page** (record view)
- **Form Page** (create/edit)
- **Settings Page** (module settings)
- **Admin Page** (admin-only screens)

### Navigation Contract (Required)

- Any module must be able to register pages with:
  - Unique route key
  - Display name
  - Module/group
  - Permission requirements
  - Optional feature flag requirements
  - If user does not have permission to view something it must not be shown
  - If user doen not have permission to perform an operation the button must not be shown.

### Error Handling

- Unknown routes show a consistent “Not Found” page.
	- 404 page must be defined
- Unauthorized routes show a consistent “Access Denied” page.
- Disabled-feature routes show a consistent “Feature Not Enabled” page.

---

## 4) Standard Views

The Application Shell must provide standardized view patterns that modules reuse.

### 4.1 Standard List View

#### Purpose

A single, consistent list experience across all entities and modules.

#### Required Capabilities

- Navigation from Header

- **Columns**

  - Configurable per list
  - Supports basic types (text, number, date/time, status)
  - Supports a primary column that opens the detail view

- **Sorting**

  - Single-column sort minimum
  - Visual indicator of active sort

- **Filtering**

  - Basic filter controls (field, operator, value)
  - Support common operators (equals, contains, starts with, date range)
  - Ability to clear filters quickly

- **Search**

  - Simple search box that searches pre-defined fields
  - Search should not require knowing field names

- **Pagination**

  - Required for performance
  - Supports page size selection (optional)

- **Row Actions**

  - View Details

- **Export & Print Hooks**

  - Export action entry point (CSV minimum in core)
  - Print action entry point

- **Header Region**

  - Section Title Center in Large font 
  - Navigation Bar bottom of header on right  

- **Footer Region**

  - Full Calendar Date in Center - Thursday, January 8, 2026
  - User Name and permission role

#### List State Persistence

- Filters/sort/search should persist when:
  - Opening a record and returning to the list
  - Navigating within the same module

Persistence scope can be per-user session at minimum.

---

### 4.2 Standard Detail View (Record View)

#### Purpose

A consistent record page for viewing and editing an object.

#### Required Layout

- **Header Region**

  - Record title / identifier
  - Status indicator (if object uses lifecycle)
  - Key metadata (created date, last updated)

- **Footer Region**

  - Key metadata (created date, last updated) (Center)
  - Full Calendar - Thursday, January 8, 2026 (Left)
  - User name and permission Role (Left)

- **Primary Actions**

  - Edit / Save / Cancel / Delete
  - Status actions (if object uses lifecycle)
  - Secondary actions menu (more actions, module operations)

- **Tabs / Sections**

  - Overview
  - Related data tabs (registered by modules)
  - Create new Related Data Record (if permitted) 
  - Documents/Notes tabs&#x20;

#### Required Capabilities

- Inline display of key fields
- Edit mode with validation messaging
- Permission-aware field editability
- Consistent empty-state messaging for tabs with no data

---

### 4.3 Standard Form View (Create/Edit)

#### Required Capabilities

- Navigation and actions are from left sidebar
- Field grouping (sections)
- Required field indicators
- Validation:
  - Inline per-field errors
  - Form-level error summary
- Save/Cancel behavior consistent across modules
- After-save navigation rule:
  - Default: go to Detail View
  - Optionally: “Save and New” (module-controlled)

---

### 4.4 Dashboard View (Optional)

The shell must support a dashboard page type.

- Main entry for the Primary Application
- Widgets are registered by modules
- Widget rendering is standardized
- Dashboard is optional per app/module

---

## 5) Action Framework

### Purpose

Standardize how actions are displayed, validated, and permission-checked.

### Action Types

- **Primary Actions** (visible buttons)
- **Secondary Actions** (dropdown / overflow menu)
- **Row Actions** (actions tied to list rows)

### Action Rules

Every action must define:

- Name/label
- Scope (list/detail/form)
- Required permission(s)
- Optional feature flag requirements
- Confirmation requirement (if destructive)
- Success/failure message behavior

### Confirmation & Warnings

- Standard confirm dialog for destructive actions
- Standard warning messaging for irreversible actions

---

## 6) Module Search (Shell-Level)

### Purpose

Provide a single entry point to search in current modules.

### Requirements

- Search bar available (top bar)
- Results grouped by object type/module
- Result item opens the appropriate detail page
- Permissions and feature flags must be respected

### Notes

The Core provides the mechanism. Modules register:

- What is searchable
- Which fields are searched
- How results are displayed

---

## 7) Notifications & Messaging Hooks (Framework Only)

The shell must include hooks for:

- Toast notifications (success/info/warn/error)
- Persistent notifications (optional later)

Core does not require implementation of business notifications.

---

## 8) Error Handling & Empty States

### Required System Pages

- Not Found
- Access Denied
- Feature Not Enabled
- System Error

### Empty-State Standards

- Lists with no results
- Detail tabs with no related records
- Search returning no matches

Each empty state must:

- Explain what happened
- Provide at least one next action (clear filter, create new, etc.) when appropriate

---

## 9) Performance & UX Requirements

### Performance

- Lists must paginate.
- Avoid loading related tabs until requested (lazy loading acceptable).
- Shell must not block navigation when optional modules are disabled.

### Usability

- Consistent keyboard behavior (enter to search, escape to close dialogs where appropriate)
- Clear loading indicators
- Consistent success/error feedback

---

## 10) Module Integration Requirements (Contract)

A module must be able to plug into the shell by registering:

- Navigation entries
- Pages/routes
- List definitions (columns, searchable fields, default filters)
- Detail tabs/sections
- Actions

The Application Shell must guarantee that:

- Modules cannot break the shell via missing registrations
- Disabled modules are fully hidden from navigation and routes
- Permission checks are consistently enforced

---

## Acceptance Criteria (Shell-Level)

- A module can be enabled/disabled without UI breakage.
- Menus reflect enabled modules and permissions.
- List view works consistently across at least two different module-provided lists.
- Detail view supports module-provided tabs.
- Module search returns results from at only the current modules.
- Standard error pages display correctly for unauthorized and unknown routes.

---

