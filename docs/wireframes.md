# Low-Fidelity Wireframes

The following ASCII wireframes capture the primary layouts for the customer search, invoice list, and item editor screens. Each screen highlights the core structure, key interactive zones, and terminology to align with business-owner feedback.

## Customer Search
```
+--------------------------------------------------------------------------------+
| Header: "Customer Manager"       [Create Customer] [Import]                   |
+--------------------------------------------------------------------------------+
| Search Bar: [🔍  Search name, email, company]  [Filters ▼]                     |
+--------------------------------------------------------------------------------+
| Filters Drawer (optional)                                                     |
|  - Status: (All • Active • Inactive)                                          |
|  - Customer Type: [Retail] [Wholesale] [Prospect]                             |
|  - Tags: [Add tag ▼]                                                          |
+--------------------------------------------------------------------------------+
| Results List                                                                  |
| +----------------------------+-----------------------------------------------+
| | Avatar | Name & Company    | Phone / Email                                 |
| +----------------------------+-----------------------------------------------+
| | •     | Dana Patel         | (555) 123-4567                                 |
| |       | Brightside Retail  | dana@brightside.com                           |
| +----------------------------+-----------------------------------------------+
| | •     | Miguel Alvarez     | (555) 987-6543                                 |
| |       | Alpine Outfitters  | miguel@alpine.com                             |
| +----------------------------+-----------------------------------------------+
| Pagination:  ‹ Prev   1  2  3   Next ›                                       |
+--------------------------------------------------------------------------------+
| Context Panel (on row select)                                                 |
|  Summary | Invoices | Notes                                                   |
|  --------------------------------------                                       |
|  - Primary contact details                                                    |
|  - Outstanding balance                                                        |
|  - Quick actions: [Create Invoice] [Add Note]                                 |
+--------------------------------------------------------------------------------+
```

## Invoice List
```
+--------------------------------------------------------------------------------+
| Header: "Invoices"            [Create Invoice] [Export CSV]                  |
+--------------------------------------------------------------------------------+
| Filters Row: Status ▼ | Date Range ▼ | Customer ▼ | Search invoices... [🔍]  |
+--------------------------------------------------------------------------------+
| Metrics Strip:  Open Balance  |  Drafts  |  Overdue                         |
|                 $24,830       |  4       |  6                               |
+--------------------------------------------------------------------------------+
| Invoice Table                                                            |
| +---------+------------+----------------------+-----------+--------------+ |
| | Status  | Invoice #  | Customer             | Due Date  | Total        | |
| +---------+------------+----------------------+-----------+--------------+ |
| | ● Overdue | INV-1042 | Brightside Retail    | Apr 10    | $1,240.00    | |
| | ● Draft   | INV-1043 | Alpine Outfitters    | Apr 15    | $980.00      | |
| | ● Paid    | INV-1041 | City Bistro          | Apr 02    | $2,150.00    | |
| +---------+------------+----------------------+-----------+--------------+ |
| Row hover actions: [View] [Send] [Mark Paid]                                |
+--------------------------------------------------------------------------------+
| Bulk Actions Bar (on selection)                                              |
|  [Send] [Mark Paid] [Delete]  |  Selected: 2 invoices                         |
+--------------------------------------------------------------------------------+
| Pagination & Density controls                                                |
+--------------------------------------------------------------------------------+
```

## Item Editor
```
+--------------------------------------------------------------------------------+
| Header: "Invoice Item"           [Duplicate] [Remove Item]                  |
+--------------------------------------------------------------------------------+
| Layout: Two-column grid                                                     |
| Column A                                                                    |
|  - Item Name          [__________________________]                          |
|  - Description        [__________________________]                          |
|  - Category ▼         [Service]                                              |
|  - Billable checkbox  [✔] Billable                                           |
|                                                                            |
| Column B                                                                    |
|  - Quantity           [ 1.0  ▼]                                             |
|  - Unit Price         [$ 150.00]                                            |
|  - Tax Rate ▼         [Standard (8.25%)]                                     |
|  - Discount           [ 0.00 %]                                             |
|                                                                            |
| Totals Strip                                                                |
|  Subtotal: $150.00   |  Tax: $12.38   |  Discount: $0.00   |  Total: $162.38 |
+--------------------------------------------------------------------------------+
| Footer                                                                       |
|  [Save Item]    [Cancel]    Validation message area                          |
+--------------------------------------------------------------------------------+
```

### Wireframe Notes
- Keep control labels literal and action-oriented to align with business-owner terminology.
- Context panels appear conditionally to provide at-a-glance business metrics without cluttering the main workflows.
- High-contrast button placement supports quick access for frequent tasks (creating invoices/customers).
