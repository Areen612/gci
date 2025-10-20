# Usability Validation Plan and Findings

## Objectives
- Confirm that navigation labels and actions match the business owner's terminology.
- Ensure that the prioritised workflows (searching, adding customers, creating invoices) are discoverable and efficient.
- Identify layout or content adjustments necessary before high-fidelity design.

## Participants
- **Primary stakeholder:** Business owner (accounting lead).
- **Facilitator:** Product designer.
- **Observer/Note-taker:** Product manager.

## Research Approach
1. **Preparation**
   - Share wireframes and user flows with the business owner 24 hours in advance.
   - Prepare a task script focusing on three core scenarios: locate an existing customer, add a new customer, and create/send an invoice.
   - Define success metrics: time to locate primary actions, number of clarification questions, and perceived confidence (self-reported 1–5 scale).
2. **Session Structure (45 minutes)**
   - Warm-up (5 min): confirm terminology, discuss current process pain points.
   - Task walkthroughs (30 min): observe owner navigating wireframes using clickable prototype or printed mockups.
   - Debrief (10 min): capture qualitative feedback, prioritize critical issues.
3. **Artifacts**
   - Annotated wireframes capturing feedback.
   - Issue log categorised by severity (blocker, major, minor).

## Iteration Summary
| Issue | Feedback | Adjustment |
|-------|----------|------------|
| Terminology | Owner prefers "Clients" over "Customers" for external relationships. | Updated navigation label to "Clients" while keeping financial reports consistent. |
| Invoice actions | Confusion between "Send" and "Share" options. | Consolidated into single "Send Invoice" CTA with tooltip explaining delivery channels. |
| Item editor totals | Totals strip was overlooked when positioned below fold. | Elevated totals strip directly under line items with sticky behavior. |
| Filter discoverability | Filters drawer icon was unclear. | Added "Filters" label next to icon and provided default chips reflecting active filters. |

## Next Steps
- Run a confirmation session after changes are applied to ensure terminology updates resonate.
- Align with development on feasibility of sticky totals strip and inline filter chips.
- Incorporate findings into UI guidelines for team-wide alignment.
