# BrixaWares Lite - Data Model Relationships

## Entity Relationship Diagram (Logical View)

```
┌─────────────────────────────────────────────────────────────────┐
│                      CORE INFRASTRUCTURE                         │
│  Users (Django), Roles, Preferences, ValueLists, Audit Logs     │
└─────────────────────────────────────────────────────────────────┘
                              ↑
                              │
┌─────────────────────────────────────────────────────────────────┐
│                         BASE MODELS                              │
│  (Foundation - Used by All Application Modules)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐                                                │
│  │   Clients    │◄────────────────┐                              │
│  └──────────────┘                 │                              │
│        │                          │                              │
│        ├─► Addresses (1:N)        │                              │
│        │   (Billing, Shipping)    │                              │
│        │                          │                              │
│        ├─► Contacts (1:N)         │                              │
│        │   └─► People (1:1)       │                              │
│        │                          │                              │
│        ├─► Phones (1:N)           │                              │
│        │   (Max 2 per Client)     │                              │
│        │                          │                              │
│        └─► Various Links          │                              │
│                                   │                              │
│  ┌──────────────┐                 │                              │
│  │  Products    │                 │                              │
│  │  (Inventory) │                 │                              │
│  └──────────────┘                 │                              │
│                                   │                              │
│  ┌──────────────┐   ┌──────────┐  │                              │
│  │    Notes     │   │Documents │  │                              │
│  └──────────────┘   └──────────┘  │                              │
│        │                 │         │                              │
│        ├─► NoteLinks     ├─► DocumentLinks                        │
│        │  (Generic: any entity)   │                              │
│                                   │                              │
└─────────────────────────────────────────────────────────────────┘
                              ↑
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
    ┌─────────┐          ┌─────────┐          ┌─────────┐
    │ PROJECTS│          │INVOICING│          │ SERVICE │
    └─────────┘          └─────────┘          └─────────┘
        │                     │                     │
        ├─ Projects          ├─ Invoices ◄────────┤
        ├─ Epics (hidden)    ├─ InvoiceLines      ├─ ServiceItems
        └─ Tasks             └─ Payments          ├─ WorkOrders
                                  ▲                └─ WorkOrderItems
                                  │                     │
                                  └─────────────────────┘
                            (Auto-created on WO Close)
        
        ┌──────────────────────────────────────────┐
        │            SALES                         │
        ├──────────────────────────────────────────┤
        ├─ Leads                                    │
        ├─ Quotes ──► QuoteLines                   │
        │     │                                    │
        │     └─ No automation to Service/Invoice  │
        └──────────────────────────────────────────┘
```

---

## Module: BASE_MODELS (Foundation)

### Clients Module
```
Client (1)
├── PK: id (UUID)
├── Fields: client_number*, name*, email, website, tax_id, notes, is_active
├── Relationships:
│   ├── addresses (1:N) → Address
│   ├── contacts (1:N) → Contact
│   ├── phones (1:N) → Phone
│   ├── projects (1:N) → Project [from projects]
│   ├── invoices (1:N) → Invoice [from invoicing]
│   ├── work_orders (1:N) → WorkOrder [from service]
│   ├── quotes (1:N) → Quote [from sales]
│   └── Notes/Documents via NoteLinks/DocumentLinks
└── Indexes: client_number, name, is_active

Address (N:1 Client)
├── PK: id (UUID)
├── FK: client_id
├── Fields: address_type (billing|shipping)*, street_line_1*, city*, state_province*, postal_code*, country*
├── Constraint: Unique(client, address_type) — 1 Billing, 0-1 Shipping per Client
└── Indexes: (client, address_type)

Contact (N:1 Client, 1:1 People)
├── PK: id (UUID)
├── FK: client_id, people_id
├── Fields: job_title, is_primary, notes
├── Relationships: phones (1:N) → Phone (Max 2 per Contact)
└── Indexes: (client, is_primary)

People (Background Only - Never in UI)
├── PK: id (UUID)
├── Fields: first_name*, last_name*, email
├── Relationships: 1:1 ↔ Contact, 1:1 ↔ User
└── Indexes: (first_name, last_name), email

Phone (N:1 Client OR N:1 Contact)
├── PK: id (UUID)
├── FK: client_id (null if Contact), contact_id (null if Client)
├── Fields: phone_number*, phone_type (mobile|office|fax|other)*
├── Validation: Exactly one of client_id or contact_id must be set
├── Constraint: Max 2 phones per Client, Max 2 per Contact
└── Indexes: client_id, contact_id
```

### Products Module
```
Product (Inventory - Exposed as Products in UI)
├── PK: id (UUID)
├── Fields: sku* (unique), name*, description, product_type*, unit_price*, unit_of_measure*
├── Relationships:
│   ├── invoice_lines (1:N) → InvoiceLine [from invoicing]
│   ├── work_order_items (1:N) → WorkOrderItem [from service]
│   └── quote_lines (1:N) → QuoteLine [from sales]
└── Indexes: sku, name, product_type
```

### Notes & Documents (Reusable Widgets)
```
Note
├── PK: id (UUID)
├── Fields: title, content*
├── Relationships: links (1:N) → NoteLink
└── Usage: Can be linked to any entity (Client, Project, Invoice, etc.)

NoteLink (Generic Linking)
├── PK: id (UUID)
├── FK: note_id
├── Fields: linked_entity_type* (app_label.model_name), linked_entity_id* (UUID)
├── Constraint: Unique(note, linked_entity_type, linked_entity_id)
├── Max Links: 5 per Note
└── Indexes: (note, linked_entity_type)

Document
├── PK: id (UUID)
├── Fields: name*, file_path*, file_size*, file_type*, description
├── Relationships: links (1:N) → DocumentLink
└── Usage: Can be linked to any entity

DocumentLink (Generic Linking)
├── PK: id (UUID)
├── FK: document_id
├── Fields: linked_entity_type* (app_label.model_name), linked_entity_id* (UUID)
├── Constraint: Unique(document, linked_entity_type, linked_entity_id)
├── Max Links: 5 per Document
└── Indexes: (document, linked_entity_type)
```

---

## Module: PROJECTS

```
Project (LifecycleModel)
├── PK: id (UUID)
├── FK: client_id
├── Fields: project_number* (unique), name*, description, start_date, end_date
├── Lifecycle: state, reason, changed_at, changed_by
├── Relationships:
│   ├── epics (1:N) → Epic
│   └── Notes/Documents via NoteLinks/DocumentLinks
├── Signal: On create → auto-creates Epic(name="General")
└── Indexes: project_number, client_id, lifecycle_state

Epic
├── PK: id (UUID)
├── FK: project_id
├── Fields: name* (e.g., "General"), description
├── Constraint: Unique(project, name)
├── Relationships: tasks (1:N) → Task
├── Note: Hidden in Lite UI; always one "General" epic per project
└── Indexes: project_id

Task (LifecycleModel)
├── PK: id (UUID)
├── FK: epic_id, assigned_to (User)
├── Fields: task_number*, title*, description, due_date, priority*
├── Lifecycle: state, reason, changed_at, changed_by
├── Priority: Low, Medium, High, Critical
├── Relationships: Notes/Documents via NoteLinks/DocumentLinks
└── Indexes: epic_id, assigned_to, lifecycle_state
```

---

## Module: INVOICING

```
Invoice (LifecycleModel)
├── PK: id (UUID)
├── FK: client_id, billing_address_id
├── Fields: invoice_number* (unique), invoice_date*, due_date, currency, notes
├── Lifecycle: lifecycle_state (Draft→Issued→Paid→Void)
├── Relationships:
│   ├── lines (1:N) → InvoiceLine
│   ├── payments (1:N) → Payment
│   ├── work_orders (1:N) → WorkOrder [from service]
│   └── Notes/Documents via NoteLinks/DocumentLinks
├── Computed: subtotal, total_amount (subtotal + tax), total_paid, balance
├── Auto-Status Rules:
│   ├── New invoices = Draft
│   ├── Sent/posted = Issued
│   ├── total_paid ≥ total_amount = Paid
│   └── Cancelled = Void
└── Indexes: invoice_number, client_id, lifecycle_state, invoice_date

InvoiceLine (1:N Invoice)
├── PK: id (UUID)
├── FK: invoice_id, product_id (optional)
├── Fields: line_type* (product|service|shipping|discount|surcharge|fee|tax|other)
├── Fields: description*, quantity*, unit_price*, amount*
├── Rule: Everything except tax is a line item (shipping, discounts, etc. = line items)
├── Amount Calc: Auto-calculated (quantity × unit_price) if not set
└── Indexes: (invoice, line_type)

Payment (1:N Invoice)
├── PK: id (UUID)
├── FK: invoice_id (required)
├── Fields: payment_date*, payment_method*, reference_number, amount*, notes
├── Payment Methods: Cash, Check, Credit Card, ACH, Other
└── Indexes: invoice_id, payment_date
```

---

## Module: SERVICE

```
ServiceItem
├── PK: id (UUID)
├── Fields: service_code* (unique), name*, description, default_rate*, unit_of_measure*
├── Relationships:
│   ├── work_order_items (1:N) → WorkOrderItem
│   └── Notes/Documents via NoteLinks/DocumentLinks
└── Indexes: service_code, name

WorkOrder (LifecycleModel)
├── PK: id (UUID)
├── FK: client_id, assigned_to (User), invoice_id (optional)
├── Fields: work_order_number* (unique), description, work_date*, notes
├── Lifecycle: lifecycle_state (e.g., Todo, In Progress, Completed, Closed)
├── Relationships:
│   ├── items (1:N) → WorkOrderItem
│   └── Notes/Documents via NoteLinks/DocumentLinks
├── Computed: total_amount (sum of items)
├── Signal: On state=Completed/Closed → auto-create Invoice (if none exists)
│   ├── Invoice.invoice_number = "AUTO-{work_order_number}"
│   ├── Invoice.client = WorkOrder.client
│   ├── Creates InvoiceLines from WorkOrderItems
│   └── Links invoice back to work_order
└── Indexes: work_order_number, client_id, lifecycle_state, work_date

WorkOrderItem (1:N WorkOrder)
├── PK: id (UUID)
├── FK: work_order_id, service_id (optional), product_id (optional)
├── Fields: item_type* (labor|material|equipment|other)
├── Fields: description*, quantity*, unit_price*, amount*
├── Amount Calc: Auto-calculated if not set
└── Indexes: work_order_id
```

---

## Module: SALES

```
Lead (LifecycleModel)
├── PK: id (UUID)
├── Fields: lead_number* (unique), company_name*, contact_name*
├── Fields: email, phone, description, estimated_value, notes
├── Lifecycle: lifecycle_state (New, Contacted, Qualified, Converted, etc.)
├── Relationships:
│   ├── quotes (1:N) → Quote
│   └── Notes/Documents via NoteLinks/DocumentLinks
└── Indexes: lead_number, lifecycle_state, company_name

Quote (LifecycleModel)
├── PK: id (UUID)
├── FK: client_id (optional), lead_id (optional)
├── Fields: quote_number* (unique), quote_date*, expiration_date
├── Fields: prospect_name, prospect_email (if not a client yet)
├── Fields: description, currency, notes
├── Lifecycle: lifecycle_state (Pending, Accepted, Rejected, etc.)
├── Relationships:
│   ├── lines (1:N) → QuoteLine
│   └── Notes/Documents via NoteLinks/DocumentLinks
├── Computed: total_amount (sum of lines)
├── Important: NO automation to Service/Invoice (Lite Rule)
└── Indexes: quote_number, client_id, lead_id, lifecycle_state, quote_date

QuoteLine (1:N Quote)
├── PK: id (UUID)
├── FK: quote_id, product_id (optional)
├── Fields: description*, quantity*, unit_price*, amount*
├── Amount Calc: Auto-calculated if not set
└── Indexes: quote_id
```

---

## Cross-Module Relationships

### Projects → Notes/Documents
```
Project →(NoteLinks)→ Note
Project →(DocumentLinks)→ Document
Task →(NoteLinks)→ Note
Task →(DocumentLinks)→ Document
```

### Invoicing → Clients/Products
```
Invoice → Client (N:1)
Invoice → Address (N:1, Billing required)
InvoiceLine → Product (N:1, optional)
```

### Service → Clients/Products/Invoices
```
WorkOrder → Client (N:1)
WorkOrder → Invoice (N:1, auto-created on Complete/Close)
WorkOrderItem → ServiceItem (N:1, optional)
WorkOrderItem → Product (N:1, optional)
```

### Sales → Clients
```
Quote → Client (N:1, optional)
Quote → Lead (N:1, optional)
QuoteLine → Product (N:1, optional)
```

### All Modules → Notes/Documents
```
Any Entity →(NoteLinks)→ Note (1-5 links)
Any Entity →(DocumentLinks)→ Document (1-5 links)
```

---

## Constraints Summary

| Entity | Constraint | Reason |
|--------|-----------|--------|
| Address | Unique(Client, AddressType) | 1 Billing, 0-1 Shipping |
| Phone | Max 2 per Client + 2 per Contact | Data quality (Lite rule) |
| Phone | Client XOR Contact | Ownership clarity |
| Epic | Unique(Project, Name) + Auto "General" | One epic per project |
| NoteLink | Unique(Note, EntityType, EntityID) | Prevent duplicate links |
| DocumentLink | Unique(Document, EntityType, EntityID) | Prevent duplicate links |
| InvoiceLines | Quantity ≥ 0, Amount can be negative | Support discounts |
| Payments | Amount > 0 | Positive payments only |

---

## Lifecycle States by Entity

| Entity | States | Transitions |
|--------|--------|------------|
| Project | Draft, Active, Completed, Archived | Any → Any |
| Task | Todo, In Progress, Done, Cancelled | Any → Any |
| Lead | New, Contacted, Qualified, Converted, Lost | Any → Any |
| Quote | Pending, Accepted, Rejected, Expired | Any → Any |
| Invoice | Draft, Issued, Paid, Void | Strict rules |
| WorkOrder | Todo, In Progress, Completed, Closed | Strict rules |

---

## Audit Trail Fields (All Entities)

```
BaseModel & LifecycleModel fields:
├── id (UUID)
├── created_at (timestamp, auto-set on create)
├── updated_at (timestamp, auto-updated on save)
├── created_by (FK to User)
├── updated_by (FK to User)
├── is_active (Boolean, soft delete support)
│
└── [If LifecycleModel:]
    ├── lifecycle_state
    ├── lifecycle_reason
    ├── lifecycle_changed_at
    └── lifecycle_changed_by

Result: Complete audit trail for compliance and troubleshooting
```

---

## Summary

- **30+ Tables** in total
- **10 Base Models** shared across all modules
- **5 Application Modules** (Core, Projects, Invoicing, Service, Sales)
- **50+ Foreign Keys** properly configured
- **40+ Database Indexes** for performance
- **20+ Unique Constraints** for data integrity
- **100% Audit Trail** on all records
- **Signal-Based Automation** (auto-epic, auto-invoice)