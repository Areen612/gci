# Invoice Feature Requirements

## User Stories
- **Invoice List Filtering**: As an accounting user, I want to view invoices filtered by customer, status, and invoice date so that I can quickly find relevant records.
- **Create Invoice**: As an accounting user, I need to create a new invoice by selecting a customer and adding multiple line items so that billing details are accurate.
- **Edit Invoice Status**: As an accounting manager, I need to update invoice statuses (draft, sent, paid, overdue, cancelled) to reflect the current lifecycle stage.
- **View Invoice Detail**: As an accounting user, I want to open a detailed view of an invoice showing customer info, totals, payments, and notes so I can verify billing information.
- **Export or Print Invoice**: As a sales or accounting user, I want to export an invoice to PDF for printing or sending to the customer.

## Implementation Tasks
- Implement list and detail views with filtering logic based on customer, status, and date range parameters.
- Create forms for invoice creation and editing, including inline formsets for managing invoice line items.
- Provide template structure for the invoice detail page showing header information, line item tables, totals, tax breakdown, and payment history.
- Configure PDF generation utilities to render invoices for export or print workflows.

## Admin Tasks
- Add inline admin for invoice line items within the Invoice admin to streamline bulk editing.
- Implement admin actions to change invoice statuses and trigger PDF regeneration when needed.
- Configure custom admin list filters for customer, status, date range, and outstanding balance.

## Search Tasks
- Enable full-text search on invoice number, customer name, and internal notes using PostgreSQL `SearchVector` or equivalent search backend.
- Add autocomplete endpoints for invoice number and customer fields in form workflows.
- Define indexes to support efficient search queries and filtering for large invoice datasets.
