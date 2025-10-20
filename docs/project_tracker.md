# Project Execution Tracker

## 1. Board Structure
- **Tool:** Jira (Kanban template) with swimlanes per epic.
- **Columns:** Backlog → Ready → In Progress → In Review → Blocked → Done.
- **Epics:**
  1. Customers
  2. Invoices
  3. Inventory
  4. Platform (DB/Test/DevOps)
- **Card fields:** Summary, Description, Acceptance Criteria, Priority, Story Points, Assignee, Start/Target Dates, Slack notification toggle.
- **Automation:** When status changes to `In Review` or `Blocked`, auto-post update to `#gci-delivery` Slack channel and email project@gci.local.

## 2. Epic Backlog Breakdown

### Customers Epic
| ID | User Story / Task | Priority | Estimate (pts) | Owner | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| CUS-01 | As a sales associate, I can search customers by name, phone, or email with typo tolerance. | P0 | 5 | Maya Lopez | Ready | Requires ElasticSearch configuration from Platform epic. |
| CUS-02 | Implement customer profile view with consolidated purchase history and loyalty status. | P0 | 8 | Daniel Osei | In Progress | Waiting on invoice API contract. |
| CUS-03 | Build customer deduplication rules and merge workflow. | P1 | 5 | Priya Nair | Backlog | Define thresholds with business owner. |
| CUS-04 | Capture preferred contact method and enforce notification opt-ins. | P1 | 3 | Maya Lopez | Backlog | Dependent on UI guideline review. |
| CUS-05 | QA test plan for customer management acceptance criteria. | P2 | 2 | Leo Fischer | Backlog | Coordinate with Platform test automation. |

### Invoices Epic
| ID | User Story / Task | Priority | Estimate (pts) | Owner | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| INV-01 | As a cashier, I can create invoices with automatic tax and discount calculations. | P0 | 8 | Priya Nair | In Progress | Tax rules defined in requirements_spec.md §3.2. |
| INV-02 | Connect invoice issuance to inventory decrement events. | P0 | 5 | Daniel Osei | Ready | Blocked until inventory webhooks available. |
| INV-03 | Generate PDF/email invoice receipts with configurable templates. | P1 | 5 | Leo Fischer | Backlog | Requires template approval. |
| INV-04 | Implement invoice status workflow with audit trail. | P0 | 5 | Maya Lopez | Ready | Aligns with compliance requirements. |
| INV-05 | UAT checklist for invoice flows. | P2 | 3 | Priya Nair | Backlog | Schedule with Week 4 review. |

### Inventory Epic
| ID | User Story / Task | Priority | Estimate (pts) | Owner | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| INVEN-01 | Build real-time stock update service and low-stock alerts. | P0 | 8 | Daniel Osei | In Progress | Needs Platform queue setup. |
| INVEN-02 | Implement bulk import for supplier delivery logs. | P1 | 5 | Leo Fischer | Ready | Parse CSV per data model. |
| INVEN-03 | Create inventory adjustment audit report. | P1 | 3 | Priya Nair | Backlog | Report spec in requirements_spec.md §5. |
| INVEN-04 | Configure reorder threshold notifications. | P1 | 3 | Maya Lopez | Backlog | Depends on INVEN-01 event stream. |
| INVEN-05 | Regression test suite for inventory changes. | P2 | 2 | Leo Fischer | Backlog | Automate via Platform CI. |

### Platform (DB/Test/DevOps) Epic
| ID | User Story / Task | Priority | Estimate (pts) | Owner | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| PLA-01 | Provision PostgreSQL schemas and role-based permissions. | P0 | 5 | Daniel Osei | In Progress | Align with data model definitions. |
| PLA-02 | Implement automated test pipelines (unit, API, end-to-end). | P0 | 8 | Leo Fischer | Ready | Use GitHub Actions + pytest/playwright. |
| PLA-03 | Set up data migration scripts for initial customer/inventory loads. | P1 | 5 | Priya Nair | Backlog | Source data in CSV per operations team. |
| PLA-04 | Configure monitoring, logging, and alerting stack. | P1 | 5 | Maya Lopez | Backlog | Hook to Slack #gci-ops. |
| PLA-05 | Create infrastructure-as-code baseline (Terraform) for staging/prod. | P1 | 8 | Daniel Osei | Backlog | Dependent on hosting decision. |

## 3. Milestones & Reviews
| Milestone | Target Week | Scope | Entry Criteria | Review Format | Notifications |
| --- | --- | --- | --- | --- | --- |
| Planning Complete | Week 2 | Confirm backlog, sizing, dependencies. | All epics have prioritized stories with estimates and owners. | 60-min walkthrough with stakeholders. | Slack: `#gci-delivery` reminder 2 days before; email agenda to leadership@gci.local. |
| Build Checkpoint | Week 3 | Demo customer search + invoice creation skeleton. | CUS-01, INV-01 in `In Review`; PLA-01 baseline done. | Live demo + Q&A. | Slack reminder 1 day before; automated email summary from meeting notes. |
| Integration Review | Week 4 | Validate invoice-inventory integration and alerting. | INV-02, INVEN-01 reach `Done`; PLA-02 pipeline green. | Recorded demo, retro on risks. | Slack & email notifications triggered via calendar event. |
| Launch Readiness | Week 6 | End-to-end flow tested, platform sign-off. | All P0 stories closed; UAT sign-off; runbook approved. | Executive review + go/no-go. | Slack broadcast @channel; email to store leadership + ops. |

## 4. Communication & Automation
- **Slack Integration:**
  - Jira automation posts to `#gci-delivery` when cards move to `In Review`, `Blocked`, or `Done`.
  - Scheduled Slack reminders via Workflow Builder every Monday 9:00 AM for standups and every Thursday 4:00 PM before sprint reviews.
- **Email Automation:**
  - Outlook group `project@gci.local` receives automated summaries after each milestone review using meeting notes template.
  - Daily digest at 6:00 PM with cards still in `Blocked` status.
- **Calendar Sync:**
  - Shared "GCI Delivery" calendar tracks milestone reviews, sprint reviews, and release windows.

## 5. Cadence & Rituals
| Ceremony | Frequency | Participants | Agenda | Owner | Notes |
| --- | --- | --- | --- | --- | --- |
| Weekly Standup | Mondays 9:30 AM | All feature owners, PM, QA | Yesterday/Today/Risks; review blockers flagged on board. | Project Manager (Sasha Kim) | Update Jira during call; Slack reminder auto-posts 15 min prior. |
| Midweek Check-in | Wednesdays Async | Feature owners | Post update thread in `#gci-delivery`; include status + ETA. | Sasha Kim | Jira automation requests update if no comment by 2 PM. |
| Sprint Review | Biweekly Thursdays 4:30 PM | Stakeholders, Feature owners | Demo completed stories, collect feedback, confirm acceptance. | Maya Lopez | Meeting notes stored in Confluence and emailed automatically. |
| Sprint Retrospective | Biweekly Thursdays 5:15 PM | Delivery team | What went well / Improve / Action items. | Leo Fischer | Action items added to Platform epic if infra-related. |
| Backlog Grooming | Tuesdays 2:00 PM | PM, Tech leads | Refine upcoming stories, adjust estimates. | Priya Nair | Prep by reviewing new requests from operations. |

## 6. Reporting & Visibility
- **Dashboards:** Jira dashboard showing burn-up chart, blocked work, and milestone countdown.
- **Standup Notes Archive:** Confluence page `GCI > Delivery > Standups` linked from board for weekly summaries.
- **Risk Register:** Add high/medium risks as labels on relevant cards and maintain summary table in Confluence.
- **Success Metrics:** Track story throughput, defect escape rate, and milestone variance weekly.

