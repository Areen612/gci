# Release 1 Scope and Backlog

## Backlog Tracker

| ID | Epic / Feature | Description | Tags |
| --- | --- | --- | --- |
| MVP-1 | Customer CRUD | Implement customer list, detail, create/update, deactivate/reactivate workflows with validation and search. | MVP |
| MVP-2 | Customer Contact Preferences | Capture preferred contact method, enforce email/phone validation rules, and surface loyalty status. | MVP |
| MVP-3 | Customer History Snapshot | Surface recent invoices and notes on customer detail view. | MVP |
| MVP-4 | Invoice History | Provide invoice listing with filters, detail view, and audit trail of status changes. | MVP |
| MVP-5 | Invoice Line Item Management | Support nested line items with tax/discount calculations when viewing invoice history. | MVP |
| MVP-6 | Inventory CRUD | Manage product records (list, detail, create/update, archive) including pricing and stock thresholds. | MVP |
| MVP-7 | Inventory Stock Adjustments | Enable manual stock adjustments tied to audit trail and validations. | MVP |
| PMVP-1 | Loyalty Program Automation | Automated rewards accrual/redemption workflows beyond displaying status. | Post-MVP |
| PMVP-2 | External Tax Service Integration | Real-time integration with third-party tax APIs. | Post-MVP |
| PMVP-3 | Payment Gateway Integration | Online payment capture and reconciliation automation. | Post-MVP |
| PMVP-4 | Reporting Dashboards | Aggregate analytics dashboards and scheduled exports. | Post-MVP |
| PMVP-5 | Supplier Management | Supplier records and purchase order tracking. | Post-MVP |
| PMVP-6 | ERP/CRM Integrations | Bi-directional sync with external inventory or CRM systems. | Post-MVP |
| PMVP-7 | Document Generation | Automated PDF invoice generation and delivery. | Post-MVP |

## Acceptance Criteria for MVP Epics

### Customer CRUD & Profile Context (MVP-1 to MVP-3)
- Staff can create a customer with required fields (first name, last name, loyalty status, preferred contact method) and optional contact details, enforcing validation rules from the requirements specification.
- Customer list supports search by name, email, or phone and returns results within 2 seconds for standard dataset sizes.
- Updating a customer preserves audit history and enforces uniqueness of email/phone when provided.
- Deactivating a customer prevents new invoices while retaining historical data; reactivation restores access without data loss.
- Customer detail page displays loyalty status, preferred contact method, and the five most recent invoices.
- Notes or comments can be added to customer records and are timestamped.

### Invoice History (MVP-4 & MVP-5)
- Users can view a paginated invoice list filtered by status, date range, and customer.
- Invoice detail shows header data, line items with subtotals, taxes, discounts, total amount, and payment method if paid.
- Status history is visible, capturing transitions (Draft → Issued → Paid/Cancelled/Refunded) with timestamps and actor information.
- Line items display linked inventory products when available; ad-hoc descriptions are supported.
- Totals match aggregated line items (including discounts and tax), with automated recalculation on edits.
- Users can access a print-friendly invoice view to support customer service follow-ups.

### Inventory CRUD & Stock Adjustments (MVP-6 & MVP-7)
- Inventory list shows key fields (SKU, name, category, stock on hand, stock reserved, reorder level) with filter by category and low stock status.
- Creating or updating an inventory item enforces validation rules (unique SKU, price >= cost, non-negative stock fields).
- Archiving an item prevents future invoice inclusion but preserves history for existing invoices.
- Manual stock adjustments require a reason code, adjust stock_on_hand and stock_reserved appropriately, and log a StockMovement record.
- Inventory detail view highlights when stock_on_hand minus stock_reserved is below reorder level and suggests reorder quantity.
- Stock changes triggered by invoices automatically adjust inventory counts to maintain real-time accuracy.

## Out-of-Scope for Release 1

To manage expectations for Release 1, the following capabilities are explicitly out of scope:

- Automated loyalty rewards calculations or tier adjustments beyond manual status updates.
- Integration with external tax or payment services; all tax/discount rules remain internal and configurable.
- Advanced reporting dashboards, scheduled exports, or data warehouse feeds.
- Supplier management, purchase order workflows, or broader supply-chain integrations.
- Automated PDF generation and digital delivery of invoices.
- Bi-directional integrations with external CRM or ERP platforms.
- Mobile-specific applications or offline mode; Release 1 focuses on the web interface only.

Stakeholders will receive progress updates aligned to the MVP backlog above, and any Post-MVP items will be revisited after Release 1 planning.
