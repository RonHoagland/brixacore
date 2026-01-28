## 🛠️ MVP Module: Preferences

### ✅ Purpose  
Store system-wide company and configuration settings that drive default behaviors, formats, and shared information across the platform.

---

### 🧱 Table Structure (Fields)

| Field Name             | Type           | Notes |
|------------------------|----------------|-------|
| `id`                   | UUID           | Auto-generated unique identifier |
| `company_name`         | String (150)   | Required |
| `address_1`            | String (100)   | Optional |
| `address_2`            | String (100)   | Optional |
| `city`                 | String (100)   | Optional |
| `state`                | String (50)    | Optional |
| `postalcode`           | String (25)    | Optional |
| `country`              | String (50)    | Optional |
| `phone_number`         | String (25)    | Optional; auto-formatted for display |
| `website`              | String (100)   | Optional |
| `logo_print`           | Image/File     | Logo used for printed documents |
| `logo_digital`         | Image/File     | Logo used for on-screen documents |
| `default_currency`     | String (5)     | Default `USD`; Values: `USD`, `PHP`, `EUR` |
| `currency_symbol`      | String (5)     | Default `$`; Values: `$`, `₱`, `€` |
| `timezone`             | String (50)    | Default `America/Chicago`; Values: `Asia/Manila`, `America/Chicago` |
| `default_phone_code`   | String (5)     | Country Code.  1, 63 |
| `default_phone_format` | String (25)    | e.g., `+63 912 345 6789` |
| `invoice_start_number` | Integer        | Used to initialize invoice auto-numbering |
| `account_start_number` | Integer        | Used to initialize account auto-numbering |
| `tax_rate`             | Decimal(5,2)   | Global tax rate; e.g., `12.00` |
| `tax_label`            | String (25)    | Display name: VAT, Sales Tax, etc. |
| `default_country`      | String (50)    | Pre-fills country in address fields |
| `decimal_precision`    | Integer        | Currency decimal rounding; e.g., `2` |
| `date_format`          | String (15)    | Default `MM/DD/YYYY`; Values: `MM/DD/YYYY`, `YYYY-MM-DD`, `DD/MM/YYYY` |
| `default_logo_height`  | Integer (px)   | For consistent layout styling |
| `default_from_email`   | String (100)   | This is the company email  |
| `smtp_host`            | String (100)   | SMTP server hostname |
| `smtp_port`            | Integer        | SMTP server port |
| `smtp_username`        | String (100)   | SMTP login username |
| `smtp_password`        | String (100)   | SMTP login password (encrypted or masked in UI) |
| `smtp_use_tls`         | Boolean        | Use TLS for SMTP |
| `smtp_use_ssl`         | Boolean        | Use SSL for SMTP |
| `created_by`           | String         | Housekeeping; Defaults to current user |
| `created_on`           | Timestamp      | Housekeeping; Defaults to now |
| `modified_by`          | String         | Housekeeping; Auto-updated |
| `modified_on`          | Timestamp      | Housekeeping; Auto-updated |

---

### 📋 Business Rules

1. Only **one active Preferences record** may exist in the system.
2. `company_name`, `default_currency`, and `invoice_start_number` are required.
3. Invoice number will increment from `invoice_start_number` on first use. Defaults to 0001.
4. Logos must be `.png`, `.jpg`, or `.svg`. Recommended sizes:  
   - `logo_print`: 300×100px  
   - `logo_digital`: 150×75px
5. SMTP settings are stored as separate fields (host, port, TLS/SSL, username, password). If a JSON package is needed for integration, it can be generated on the backend as required.
6. Editing restricted to Admins or users with `System Configuration` permissions
7. When the Default Currency and Currency Symbol are selected they should match countries.
8. Phone number formatting should be consistent with the selected country.
9. Date format should be consistent with the selected country.
10. Currency formatting (symbol, decimal places) should align with the selected country.
11. decimal_precision should default to 2.
12. account_start_number will increment from entry on first use.  Defaults to 0001.
13. Once a currency has been set it cannot be changed if there are any invoices.

---

### 🧠 Auto-Populate / Defaults

- `id`: Generated UUID
- `created_by` / `modified_by`: Current user
- `created_on` / `modified_on`: System timestamps
- `country` / `default_country`: Based on install or admin selection
- `currency_symbol`: Derived from `default_currency`, but editable
- `decimal_precision`: Defaults to `2`
- `timezone`: Based on initial system setup

---

### 💻 UI/UX Considerations

- Preferences accessed via Admin → System Settings panel.
- Inline field editing with section tabs (Company Info, Financial, Branding, Communication).
- Logo fields support drag & drop and thumbnail previews.
- `invoice_start_number` field becomes read-only after first invoice is generated.
- Timezone and currency auto-suggest based on locale.
- JSON SMTP settings may be entered manually or via guided form.