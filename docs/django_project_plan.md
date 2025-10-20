# Django Project Architecture Plan

## Application Breakdown

| App | Purpose | Key Models | Key Relationships |
| --- | ------- | ---------- | ----------------- |
| customers | Manage customer profiles, contacts, and account preferences. | `Customer`, `ContactMethod`, `CustomerNote` | Customers have many contact methods and notes; invoices reference customers. |
| invoices | Handle invoicing lifecycle from draft to payment, including line items and tax calculations. | `Invoice`, `InvoiceLine`, `Payment`, `InvoiceStatusHistory` | Invoice belongs to customer; invoice lines reference inventory items or ad-hoc descriptions; payments tie to invoices; taxes integrate via service boundary. |
| inventory | Track products/services offered, pricing, tax categories, and stock levels. | `Product`, `TaxCategory`, `StockMovement` | Products belong to tax categories; invoice lines reference products; stock movements created from invoices or manual adjustments. |
| reporting | Provide aggregate metrics, exports, and scheduled reports. | (May be virtual models or query sets) | Consumes data from other apps; minimal direct relationships. |
| core | Shared utilities, settings, and common components (e.g., base models, mixins). | `TimestampedModel`, `Address`, `Currency` | Abstract models reused across apps. |

Optional future apps: `integrations` (external services), `billing` (subscriptions), `support` (tickets).

## CRUD Flows and UI Mapping

### Customers App

- **List View**: `CustomerListView` (class-based, paginated, searchable). Template: `customers/customer_list.html`. Provides filters (status, tags), search bar (AJAX or GET query) hitting `customers:search` view returning JSON.
- **Detail View**: `CustomerDetailView`. Template: `customers/customer_detail.html`. Displays summary, recent invoices, notes. Tabs for activity, contacts.
- **Create/Update Forms**: `CustomerForm` (ModelForm). Views: `CustomerCreateView`, `CustomerUpdateView`. Templates: `customers/customer_form.html`. Includes inline formsets for contact methods, addresses.
- **Delete View**: `CustomerDeleteView` with confirmation template `customers/customer_confirm_delete.html`. Soft-delete via `is_active` flag to preserve history.
- **Search API**: `CustomerSearchView` (class-based, inherits from `ListView` or DRF `APIView`). Returns JSON with `id`, `name`, `email` for autocomplete components.

### Invoices App

- **Invoice List**: `InvoiceListView` with filters (status, date range, customer). Template: `invoices/invoice_list.html`. Supports bulk actions (export, status change).
- **Invoice Detail**: `InvoiceDetailView`. Template: `invoices/invoice_detail.html`. Shows header, customer info, line items, payment history, audit trail.
- **Create/Update**: `InvoiceForm` with nested `InvoiceLineFormSet`. Views: `InvoiceCreateView`, `InvoiceUpdateView`. Template: `invoices/invoice_form.html`. Auto-calculates totals, tax, due date.
- **Delete/Cancel**: `InvoiceCancelView` to mark invoices as cancelled (soft delete). Confirmation template `invoices/invoice_cancel_confirm.html`.
- **Payment Recording**: `PaymentForm` via `PaymentCreateView`. Template: `invoices/payment_form.html`. Optionally triggered from invoice detail.
- **Status History**: `InvoiceStatusTimelineView` for audit logging (AJAX endpoint returning JSON timeline).

### Inventory App

- **Product List**: `ProductListView` with stock filter. Template: `inventory/product_list.html`.
- **Product Detail**: `ProductDetailView`. Template: `inventory/product_detail.html` with stock levels, sales metrics.
- **Create/Update**: `ProductForm`. Views: `ProductCreateView`, `ProductUpdateView`. Template: `inventory/product_form.html`. Supports uploading images, setting price tiers.
- **Delete**: `ProductDeleteView`. Template: `inventory/product_confirm_delete.html`. Soft delete or archived state.
- **Stock Movements**: `StockMovementListView`, `StockAdjustmentFormView` for manual adjustments. Templates: `inventory/stockmovement_list.html`, `inventory/stock_adjustment_form.html`.

### Reporting App

- **Dashboard View**: `ReportingDashboardView`. Template: `reporting/dashboard.html` showing summary metrics and charts.
- **Exports**: `ReportExportView` generating CSV/PDF. Template: `reporting/export.html` for selecting parameters.

## Forms and Templates Structure

```
project/
  customers/
    forms.py
    views/
      __init__.py
      customer.py
    templates/customers/
      customer_list.html
      customer_detail.html
      customer_form.html
      customer_confirm_delete.html
      components/
        search_results.html
  invoices/
    forms.py
    views/
      invoice.py
      payment.py
    templates/invoices/
      invoice_list.html
      invoice_detail.html
      invoice_form.html
      invoice_cancel_confirm.html
      payment_form.html
  inventory/
    forms.py
    views/product.py
    templates/inventory/
      product_list.html
      product_detail.html
      product_form.html
      product_confirm_delete.html
      stockmovement_list.html
  reporting/
    views.py
    templates/reporting/dashboard.html
```

- Shared templates (layouts, components) under `templates/shared/`.
- Use Django Crispy Forms or Tailwind for consistent styling.

## Customer Search Flow

1. **Frontend**: Search bar component in customer list template. Debounced input sending GET requests to `/customers/search/?q=...`.
2. **View**: `CustomerSearchView` returning JSON or HTML partial. Could subclass `ListView` with `application/json` response.
3. **Query**: Use `SearchVector` (Postgres) or `icontains` fallback. Index fields `name`, `email`, `company`, `phone`.
4. **Response**: JSON with `results: [{"id": 1, "display": "Acme Corp (acme@example.com)"}, ...]` for autocomplete dropdown.
5. **Permissions**: Require `customers.view_customer` permission; throttle API for rate limiting.
6. **Tests**: Unit tests for search view ensuring query filtering, permission enforcement.

## Authentication & Authorization Strategy

- **Authentication**: Use Django Auth with email/username login. Enforce strong passwords via `AUTH_PASSWORD_VALIDATORS`. Support optional SSO (social auth) via dedicated app.
- **User Model**: Custom user extending `AbstractUser` to add fields like `company`, `timezone`. Place in `core` app.
- **Groups**:
  - `Sales` – view/create customers and invoices, cannot delete invoices.
  - `Accounting` – full invoice/payment management, can approve/cancel invoices.
  - `InventoryManagers` – manage inventory, adjust stock.
  - `Admins` – full access, manage users and settings.
- **Permissions**:
  - `customers` app: `view_customer`, `add_customer`, `change_customer`, `deactivate_customer` (custom). Restrict delete; prefer `is_active` toggle.
  - `invoices`: `view_invoice`, `add_invoice`, `change_invoice`, `cancel_invoice`, `record_payment`.
  - `inventory`: `view_product`, `add_product`, `change_product`, `archive_product`, `adjust_stock`.
  - `reporting`: `view_reporting_dashboard`, `export_reports`.
- **Authorization Implementation**:
  - Use `PermissionRequiredMixin` for class-based views.
  - Employ object-level permissions for invoices tied to assigned sales rep (via `django-guardian` if needed).
  - Add middleware to enforce 2FA for privileged groups.
  - Expose `@login_required` across all CRUD views.
  - Provide admin screens for managing groups/permissions.

## Service Boundaries & Integrations

| Service | Boundary Description | Integration Considerations |
| ------- | -------------------- | -------------------------- |
| Tax Calculation Service | Isolate tax logic in `invoices.services.tax` with interface `TaxCalculator`. Allows swapping between manual rates and external API (e.g., Avalara). | Use adapter pattern. Store tax transaction IDs on invoice. Provide async job for recalculations. Handle API failures gracefully with retries and fallbacks. |
| Payment Gateway | Encapsulate payment processing in `invoices.services.payments`. Manage tokens, refunds, webhooks. | Use Django signals or Celery tasks to update invoice status on webhook. Separate credentials per environment. |
| Inventory Systems | Interface via `inventory.integrations.erp`. Sync product data and stock levels. | Provide data mappers; store sync logs; allow manual override. |
| CRM/Marketing | `customers.integrations.crm` handles push/pull of customer records. | Use Celery for background sync. Respect GDPR/consent fields. |
| Document Generation | `invoices.services.documents` to render PDFs via template + WeasyPrint. | Caches generated documents; store file references in storage service. |

- Each service module exposes high-level functions; Django apps depend on interfaces, not implementations.
- Configure via `settings.py` with environment-specific options. Use dependency injection (e.g., `django-appconf` or simple factory) for selecting real vs. mock services.
- Logging & Monitoring: centralized logging per service boundary, structured logs with correlation IDs.
- Testing: Provide fake adapters in `tests/fakes/` to simulate external services.

## Data Flow & Events

- When invoice created: create invoice, reserve stock via `inventory` service, calculate taxes, send notification event (Celery task).
- Payments: on webhook, validate signature, update invoice status, append `Payment` record, trigger receipt email.
- Customer updates: propagate to CRM integration asynchronously.
- Stock adjustments: record `StockMovement`, optionally push to ERP.

## Future Considerations

- Multi-company support via `Company` model linking to customers/invoices/inventory.
- Feature flags for beta features (e.g., new tax engine).
- API layer (Django REST Framework) for integrations. Consider separate `api` app with versioning.
- Audit logging using `django-simple-history` or custom `AuditLog` model in `core` app.
- Background jobs handled via Celery + Redis. Structured tasks per domain app.

