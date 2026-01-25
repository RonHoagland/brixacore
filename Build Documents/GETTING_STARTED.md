# BrixaWares Lite - Getting Started Guide

## Quick Start

### 1. Activate Virtual Environment
```bash
cd /Volumes/SolDev_10/Brixa/brixaware/brixacore
source venv/bin/activate
```

### 2. Create Admin User
```bash
python manage.py createsuperuser
# Follow prompts to create username, email, password
```

### 3. Run Development Server
```bash
python manage.py runserver
# Server starts at http://127.0.0.1:8000/
# Admin panel at http://127.0.0.1:8000/admin/
```

### 4. Log In to Admin
- Go to http://127.0.0.1:8000/admin/
- Use credentials created in step 2
- You now have access to all 30+ models

---

## Admin Interface Walkthrough

### Overview of Available Models

#### BASE MODELS (Shared Foundation)
- **Clients** - Your customers
- **Addresses** - Billing/shipping addresses
- **Contacts** - People at client organizations
- **Phones** - Contact phone numbers
- **Products** - Your product/service catalog
- **Notes** - Reusable notes (can attach to any module)
- **Documents** - Reusable documents (can attach to any module)

#### PROJECTS
- **Projects** - Project containers
- **Epics** - Hidden in UI (one "General" per project)
- **Tasks** - Work items with assignments and due dates

#### INVOICING
- **Invoices** - Billing documents
- **Invoice Lines** - Line items on invoices
- **Payments** - Payment records

#### SERVICE
- **Service Items** - Service catalog
- **Work Orders** - Work execution documents
- **Work Order Items** - Labor/materials on work orders

#### SALES
- **Leads** - Prospect intake
- **Quotes** - Sales proposals
- **Quote Lines** - Line items on quotes

---

## Common Tasks

### Creating a New Client

1. Go to Admin → BASE_MODELS → Clients
2. Click "Add Client"
3. Fill in:
   - **Client Number**: e.g., "C-001" (required, must be unique)
   - **Name**: e.g., "Acme Corporation" (required)
   - **Email**: (optional)
   - **Website**: (optional)
   - **Tax ID**: (optional)
   - **Notes**: Any internal notes
4. Click "Save"

The client is now created and available for use in Projects, Invoices, Work Orders, and Quotes.

### Adding an Address to a Client

1. Go to Admin → BASE_MODELS → Addresses
2. Click "Add Address"
3. Select the Client
4. Choose Address Type: "Billing" or "Shipping"
   - Note: A client can have 1 Billing + 0-1 Shipping
5. Fill in address fields
6. Click "Save"

### Adding a Contact to a Client

1. Go to Admin → BASE_MODELS → Contacts
2. Click "Add Contact"
3. You must first create a **People** record:
   - Go to Admin → BASE_MODELS → People
   - Click "Add People"
   - Fill in First Name, Last Name, Email
   - Click "Save"
4. Back to Contacts, select:
   - The People record just created
   - The Client
   - Job Title (optional)
   - Is Primary? (checkbox)
5. Click "Save"

### Creating a Product

1. Go to Admin → BASE_MODELS → Products
2. Click "Add Product"
3. Fill in:
   - **SKU**: e.g., "INSTALL-001" (required, unique)
   - **Name**: e.g., "Installation Service" (required)
   - **Description**: What this product is
   - **Product Type**: Service, Material, Equipment, Other
   - **Unit Price**: e.g., "75.00"
   - **Unit of Measure**: e.g., "hour" or "each"
4. Click "Save"

### Creating a Project

1. Go to Admin → PROJECTS → Projects
2. Click "Add Project"
3. Fill in:
   - **Project Number**: e.g., "PROJ-001" (required, unique)
   - **Name**: e.g., "Office Renovation" (required)
   - **Client**: Select from dropdown
   - **Start Date**: (optional)
   - **End Date**: (optional)
   - **Description**: Project details
   - **Lifecycle State**: Draft, Active, etc.
4. Click "Save"

**Important**: When you save, a "General" epic is automatically created for this project.

### Creating a Task

1. Go to Admin → PROJECTS → Tasks
2. Click "Add Task"
3. Fill in:
   - **Epic**: Select "General" epic under the project
   - **Task Number**: e.g., "PROJ-001-001" (required, unique)
   - **Title**: e.g., "Install fixtures" (required)
   - **Description**: Details
   - **Assigned To**: Select a user (optional)
   - **Due Date**: (optional)
   - **Priority**: Low, Medium, High, Critical
   - **Lifecycle State**: Todo, In Progress, Done, etc.
4. Click "Save"

### Creating an Invoice

1. Go to Admin → INVOICING → Invoices
2. Click "Add Invoice"
3. Fill in:
   - **Invoice Number**: e.g., "INV-001" (required, unique)
   - **Client**: Select client (required)
   - **Billing Address**: Select from client's addresses (required for Lite)
   - **Invoice Date**: Default is today
   - **Due Date**: (optional)
   - **Currency**: Default "USD"
   - **Lifecycle State**: Draft
   - **Notes**: (optional)
4. Click "Save"
5. You'll see two inline sections:
   - **Invoice Lines** - Click "Add another Invoice Line"
   - **Payments** - Click "Add another Payment"

### Adding Invoice Lines

1. In the Invoice Lines section, click "Add another Invoice Line"
2. Fill in:
   - **Line Type**: Product, Service, Shipping, Discount, etc.
   - **Product**: (optional, for tracking)
   - **Description**: e.g., "Installation Labor"
   - **Quantity**: e.g., "8"
   - **Unit Price**: e.g., "75.00"
   - **Amount**: Auto-calculated from Quantity × Unit Price
3. Add multiple lines as needed
4. Click "Save" at bottom

Invoice totals (subtotal, total, balance) are calculated automatically.

### Recording a Payment

1. In the Payments section of an Invoice, click "Add another Payment"
2. Fill in:
   - **Payment Date**: Default is today
   - **Payment Method**: Cash, Check, Credit Card, ACH, Other
   - **Reference Number**: e.g., check number, transaction ID
   - **Amount**: Amount received
   - **Notes**: (optional)
3. Click "Save"

The invoice will automatically mark as "Paid" when total payments ≥ invoice total.

### Creating a Work Order

1. Go to Admin → SERVICE → Work Orders
2. Click "Add Work Order"
3. Fill in:
   - **Work Order Number**: e.g., "WO-001" (required, unique)
   - **Client**: Select from dropdown (required)
   - **Description**: Work scope
   - **Work Date**: Default is today
   - **Assigned To**: Select user (optional)
   - **Lifecycle State**: Todo, In Progress, Completed, etc.
   - **Notes**: Work results/notes
4. Click "Save"
5. Add Work Order Items:
   - Click "Add another Work Order Item"
   - Select Item Type (Labor, Material, Equipment, Other)
   - Fill in Description, Quantity, Unit Price
6. Click "Save"

**Important**: When you change Lifecycle State to "Completed" or "Closed" and save:
- An Invoice is automatically created (if one doesn't exist)
- All work order items become invoice lines
- Invoice number: "AUTO-{work_order_number}"
- You can then record payments on that invoice

### Creating a Quote

1. Go to Admin → SALES → Quotes
2. Click "Add Quote"
3. Fill in:
   - **Quote Number**: e.g., "QUOTE-001" (required, unique)
   - **Quote Date**: Default is today
   - **Expiration Date**: When quote expires (optional)
   - **Client**: (optional - for existing customers)
   - **Lead**: (optional - for prospects from leads)
   - **Prospect Name**: (if not a client yet)
   - **Prospect Email**: (if not a client yet)
   - **Description**: Quote scope
   - **Currency**: Default "USD"
4. Click "Save"
5. Add Quote Lines:
   - Click "Add another Quote Line"
   - Fill in Description, Quantity, Unit Price
   - Amount auto-calculates
6. Click "Save"

---

## Key Business Rules to Remember

### Addresses
- A Client can have **1 Billing address**
- A Client can have **0-1 Shipping address**
- Invoices require a Billing address

### Phones
- Max **2 phones per Client**
- Max **2 phones per Contact**
- Each phone must belong to EITHER a Client OR Contact (not both)

### Epics (Projects)
- **Hidden in Lite UI** (but exist in database)
- One "General" epic is auto-created per project
- All tasks must attach to an epic (usually "General")

### Invoices
- **Statuses**: Draft → Issued → Paid → Void
- **Line items**: All charges/discounts are line items (including shipping, discounts)
- **Tax**: Stored as separate line type
- **Auto-paid**: Invoice automatically marked "Paid" when total payments ≥ total amount

### Work Orders
- **Auto-invoice**: When marked Completed/Closed, an Invoice is automatically created
- Copies all work order items as invoice lines
- Invoice number format: "AUTO-{work_order_number}"

### Quotes
- **Terminal** (no follow-up opportunities)
- **No automation** to Service or Invoice modules
- Can be for existing clients or prospects
- For tracking prospects, create them as Leads first

---

## Admin Interface Features

### List Views
All list views include:
- **Search** (use the search box at top)
- **Filters** (sidebar filters on right)
- **Sort** (click column headers)
- **Actions** (select items and choose actions)

### Inline Editing
Some models allow inline editing of related items:
- **Invoice**: Edit Invoice Lines and Payments inline
- **Work Order**: Edit Work Order Items inline
- **Quote**: Edit Quote Lines inline

### Read-Only Fields
These fields are automatically maintained and can't be edited:
- ID (UUID)
- created_at, updated_at (timestamps)
- created_by, updated_by (user attribution)
- lifecycle_changed_at, lifecycle_changed_by (for Lifecycle models)

---

## Sample Data for Testing

### Quick Setup Script
```python
# python manage.py shell
from django.contrib.auth.models import User
from base_models.models import Client, People, Contact, Address, Phone, Product
from projects.models import Project, Task
from invoicing.models import Invoice, InvoiceLine
from service.models import ServiceItem, WorkOrder
from sales.models import Lead, Quote

# Get or create test user
user = User.objects.first()  # Use superuser created earlier

# Create test client
client = Client.objects.create(
    client_number="TEST-001",
    name="Test Client Inc",
    email="test@example.com",
    created_by=user,
    updated_by=user
)

# Create address
address = Address.objects.create(
    client=client,
    address_type="billing",
    street_line_1="123 Main St",
    city="Springfield",
    state_province="IL",
    postal_code="62701",
    country="USA",
    created_by=user,
    updated_by=user
)

# Create product
product = Product.objects.create(
    sku="TEST-SVC-001",
    name="Test Service",
    product_type="service",
    unit_price=100.00,
    unit_of_measure="hour",
    created_by=user,
    updated_by=user
)

print("✅ Sample data created successfully")
```

---

## Testing & Verification

### Run Tests
```bash
python manage.py test
# Output: Ran 51 tests... OK
```

### Check Database
```bash
python manage.py dbshell
# Then run SQL queries
```

### Create Sample Data (via admin)
1. Log in to admin
2. Create a test client
3. Add an address
4. Create a product
5. Create a project
6. Create a task
7. Create an invoice

---

## Troubleshooting

### "User matching query does not exist"
- **Cause**: created_by or updated_by user doesn't exist
- **Solution**: Pass `created_by=request.user` in views (handled automatically in forms)

### "IntegrityError: UNIQUE constraint failed"
- **Cause**: Trying to create duplicate of unique field (e.g., client_number)
- **Solution**: Use unique numbers/codes

### Phone validation error
- **Cause**: Phone belongs to both Client and Contact
- **Solution**: Set either client_id OR contact_id, not both

### Work Order auto-invoice not created
- **Cause**: Lifecycle state not changed to "Completed" or "Closed"
- **Solution**: Change lifecycle_state and save

---

## Next Steps

1. ✅ **Load sample data** (via admin or script above)
2. ✅ **Test all modules** (create records and verify relationships)
3. ⏳ **Build frontend views** (list/detail pages for each module)
4. ⏳ **Implement permissions** (role-based access control)
5. ⏳ **Create reports** (filtered lists with CSV export)
6. ⏳ **Add business logic** (custom validations, workflows)

---

## Support

Refer to:
- [BUILD_STATUS.md](BUILD_STATUS.md) - Implementation overview
- [DATA_MODEL_RELATIONSHIPS.md](DATA_MODEL_RELATIONSHIPS.md) - Schema details
- [Model docstrings](../brixacore/) - In-code documentation
- Build Documents folder - Original specifications