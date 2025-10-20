# QA Test Plan

This plan outlines manual regression scripts, exploratory testing sessions, and the defect reporting workflow for the GCI store operations platform.

## 1. Manual Test Scripts

Each script assumes the tester signs in with role-appropriate credentials and has access to audit logs for validation. Record actual results and attach screenshots or logs in the test management tool.

### 1.1 Admin CRUD Management

| Test ID | Preconditions | Steps | Expected Result | Notes |
| --- | --- | --- | --- | --- |
| ADM-CRUD-01 | Admin dashboard accessible; at least one role (`Sales`, `Accounting`, `InventoryManagers`) defined. | 1. Navigate to **Admin → Users**.<br>2. Click **Create User** and complete mandatory fields.<br>3. Assign `Admins` role and save. | New admin user appears in list with correct role; welcome email/job queued. | Verify password policy errors shown for weak inputs.
| ADM-CRUD-02 | Existing admin user created in ADM-CRUD-01. | 1. Open the user's detail page.<br>2. Edit contact info and toggle `is_staff` permissions.<br>3. Save changes. | Updated values persist; change logged in audit trail. | Confirm last login untouched when profile-only changes occur.
| ADM-CRUD-03 | Target admin user exists with no pending tasks. | 1. Open user detail page.<br>2. Click **Deactivate**.<br>3. Confirm action. | User flagged inactive; unable to sign in; deactivation recorded with timestamp. | Attempt login with deactivated account to confirm lockout message.
| ADM-CRUD-04 | Signed in as non-admin (e.g., `Sales`). | 1. Attempt to access **Admin → Users** URL directly.<br>2. Try POST to user creation endpoint via browser dev tools or API client. | Access denied (HTTP 403) and event logged. | Capture log entry ID for security review.

### 1.2 Invoice Creation and Lifecycle

| Test ID | Preconditions | Steps | Expected Result | Notes |
| --- | --- | --- | --- | --- |
| INV-CRT-01 | Customer exists; at least one active inventory item with tax category. | 1. Navigate to **Invoices → Create**.<br>2. Select customer and add two line items.<br>3. Apply loyalty discount and submit. | Invoice saved as `Draft`; subtotal, tax, discount, total auto-calculated. | Validate rounding rules using requirements in tax service spec.
| INV-CRT-02 | Draft invoice from INV-CRT-01. | 1. Click **Issue Invoice**.<br>2. Record payment with `Card` method.<br>3. View invoice detail. | Status transitions to `Paid`; payment record stored; stock reserved quantities reduced. | Confirm due date recalculates when status changes.
| INV-CRT-03 | Issued invoice with unpaid balance. | 1. Click **Cancel Invoice**.<br>2. Provide cancellation reason and confirm. | Invoice status becomes `Cancelled`; stock reservations released; cancellation appears in history. | Ensure notification sent to accounting channel.
| INV-CRT-04 | Paid invoice. | 1. Attempt to edit line items.<br>2. Save updates. | System blocks edit with validation message referencing immutable paid invoices. | Attach screenshot of warning for regression history.

### 1.3 Inventory Stock Adjustments

| Test ID | Preconditions | Steps | Expected Result | Notes |
| --- | --- | --- | --- | --- |
| INV-STK-01 | Inventory manager role; product with stock_on_hand `50`. | 1. Navigate to **Inventory → Stock Adjustment**.<br>2. Choose product and set adjustment `+10` with reason `Restock`.<br>3. Submit. | Stock_on_hand updates to `60`; stock movement entry recorded with positive delta. | Verify audit log captures user, timestamp, and reason.
| INV-STK-02 | Product from INV-STK-01 currently `60` units. | 1. Create adjustment `-5` reason `Shrinkage`.<br>2. Save and view movement list. | Stock_on_hand becomes `55`; movement entry flagged as negative with required justification. | Confirm cannot reduce below zero using validation.
| INV-STK-03 | Product has `stock_reserved` `10` with `stock_on_hand` `55`. | 1. Attempt adjustment `-50`.<br>2. Submit form. | Validation prevents change; error cites reserved stock constraint. | Capture system message for documentation.
| INV-STK-04 | Product with low-stock threshold `20`, current stock `18`. | 1. View product detail after adjustment.<br>2. Trigger low-stock alert workflow if not auto-sent. | Low-stock alert displayed and notification job queued. | Confirm integration event enqueued (Celery or webhook).

## 2. Exploratory Test Sessions

Schedule 90-minute charters aligned to delivery milestones. Debrief immediately after each session to log observations and follow-up actions.

| Milestone | Feature Focus | Charter | Roles | Target Window | Environment & Data | Reporting |
| --- | --- | --- | --- | --- | --- | --- |
| M1 – Admin Foundations | User management, permission gating | Explore edge cases around creating, editing, and deactivating staff accounts; stress-test role assignments. | QA lead (driver), Security analyst (observer) | Week 2 post-admin MVP deployment | Staging build `v0.3.0`; seeded users across all roles; audit log viewer enabled. | Debrief doc + mind map in Confluence; create issues in tracker within 24h. |
| M2 – Billing Core | Draft→Issue→Pay invoice lifecycle | Probe calculations with extreme discounts/taxes and multi-line invoices; verify notifications and stock linkage. | QA lead (driver), Finance SME (observer) | Week 4 after invoice module code freeze | Staging build `v0.5.0`; dataset with taxable/non-taxable items; payment gateway sandbox keys. | Session notes attached to invoice epic; defects logged same day. |
| M3 – Inventory Control | Manual stock moves, low-stock alerts | Investigate reconciliation scenarios, rapid adjustments, and concurrent edits. | QA (driver), Inventory manager (observer) | Week 6 before inventory release candidate | Pre-prod `v0.7.0`; products with varying thresholds; webhook monitor running. | Charter report stored in QA SharePoint; sync highlights at sprint review. |
| M4 – End-to-End Readiness | Cross-app workflows (admin→invoice→inventory) | Follow realistic sales day narrative to uncover integration gaps and audit readiness. | QA lead (driver), Product owner (observer) | Week 8 ahead of UAT kickoff | Pre-prod `v1.0.0-rc`; anonymized production-like data; monitoring dashboards available. | Publish findings in release readiness report; escalate blockers via release checklist. |

## 3. Issue Tracking and Reproduction Steps

1. Capture defects in the central tracker (Jira or Linear) using the "QA Defect" issue type.
2. Include reproduction steps as numbered actions using consistent data references (e.g., customer `CUST-1023`).
3. Attach supporting evidence (screenshots, HAR files, console logs) and link to failing test script ID or exploratory session charter.
4. Tag the owning squad and set severity based on customer impact and workaround availability.

### Issue Template

```
Summary: <Concise failure description>
Component: <Admin | Invoices | Inventory | Cross-App>
Severity: <Critical | High | Medium | Low>
Environment: <e.g., Staging v0.5.0>
Detected By: <Tester name/date>

Preconditions:
- <Data setup or account state>

Reproduction Steps:
1. <Step one>
2. <Step two>
3. <Step three>

Expected Result:
- <Describe requirement-aligned behavior>

Actual Result:
- <Describe observed failure>

Attachments:
- <Links to screenshots/logs>
Related Test Script / Charter: <ID>
```

Maintain an issue triage log reviewing new defects within 24 hours, ensuring ownership is assigned, and linking fixes to regression scripts for future runs.
