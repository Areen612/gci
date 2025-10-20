# User Flows

These flows outline the primary actions for customer search, customer creation, and invoice creation, including key decision points and system responses.

## Search for a Customer
1. **Entry Point:** User lands on Customer Search screen from navigation menu or after login.
2. User focuses the search bar; placeholder "Search name, email, company" clarifies supported fields.
3. User types query and presses Enter or selects a suggested result.
4. **System:** Performs instant search, highlights matching text within the Results List.
5. User optionally opens Filters drawer to refine by Status, Customer Type, or Tags.
6. **Decision:**
   - If results are found, user reviews summary panel or opens customer details.
   - If no results, system shows empty state with CTA: "Create Customer".
7. User selects a result to view context panel with quick actions (Create Invoice, Add Note).

## Add a New Customer
1. **Entry Point:** User clicks "Create Customer" on Customer Search screen or header.
2. Modal/wizard opens with sections: Contact Info, Company, Billing.
3. User completes required fields (Name, Email) and optional ones (Phone, Tags).
4. Validation runs inline; errors highlighted next to fields with guidance.
5. User reviews summary, toggles "Send welcome email" option.
6. User clicks "Save Customer".
7. **System:** Saves record, closes modal, and displays success toast.
8. Customer list refreshes with new entry selected; context panel appears for quick follow-up actions.

## Create an Invoice
1. **Entry Point:** User clicks "Create Invoice" from header or customer context panel.
2. Invoice editor opens with customer pre-filled when launched from a customer.
3. User enters invoice metadata: Issue Date, Due Date, Payment Terms.
4. User adds items via "Add Line Item" button, opening Item Editor.
5. Within Item Editor, user specifies name, description, quantity, price, tax, and discount.
6. User saves item, returning to invoice summary with recalculated totals.
7. User can adjust invoice-level notes, footer, and attachments.
8. **Decision:**
   - Save as Draft: stores invoice without sending, status "Draft".
   - Send Invoice: opens preview modal to confirm email recipients and message.
9. Upon confirmation, system sends invoice email, marks status accordingly, and records activity log entry.
10. Success toast appears; user can view invoice or return to list.

### Flow Considerations
- Auto-save partial progress every 30 seconds to prevent data loss.
- Provide breadcrumb navigation for context within multi-step forms.
- Maintain consistent success/error messaging to reinforce mental model.
