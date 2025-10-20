# UI Guidelines

These guidelines ensure consistency across upcoming high-fidelity designs derived from the low-fidelity wireframes.

## Brand Foundations
- **Voice:** Professional, clear, and supportive—prioritize action verbs and financial clarity.
- **Terminology:** Use "Client" for customer-facing labels, "Invoice" for billing documents, "Item" for line entries.

## Color Palette
| Usage | Color | Hex | Notes |
|-------|-------|-----|-------|
| Primary action | Deep Blue | `#2456A6` | Buttons such as "Create Invoice" and "Save Item".
| Secondary action | Slate Gray | `#5A6B7B` | Secondary buttons, filter toggles.
| Accent/Status Positive | Emerald | `#1F9D55` | Paid status chips, success toasts.
| Accent/Status Warning | Amber | `#F6A609` | Overdue indicators, warning banners.
| Accent/Status Critical | Crimson | `#D64541` | Error states, destructive actions.
| Background | Off-White | `#F7F9FB` | Page backgrounds to reduce glare.
| Surface | Pure White | `#FFFFFF` | Cards, tables, modals.
| Divider | Light Gray | `#E2E8F0` | Table borders, separators.

## Typography
- **Primary Typeface:** Inter (or system fallback Segoe UI, Helvetica, Arial).
- **Hierarchy:**
  - H1 (Page titles): 28px, Semi-bold, `#1F2A44`.
  - H2 (Section titles): 22px, Semi-bold, `#1F2A44`.
  - Body: 16px, Regular, `#2F3B52`.
  - Supporting/Meta: 14px, Medium, `#5A6B7B`.
- Maintain 150% line height for readability.

## Spacing & Layout
- Base spacing unit: **8px**.
- Use multiples of 8px for padding/margins; 24px section padding, 16px element spacing, 12px between related controls.
- Responsive layout grid: 12 columns with 24px gutters for desktop; collapse to 4-column grid on mobile.
- Keep primary action buttons aligned to the right on desktop and full-width on mobile.

## Components
- **Search Bar:** Full-width with pill-shaped container, includes leading icon and optional filter badge.
- **Tables:** Zebra striping every other row, 16px cell padding, sticky header with shadow.
- **Context Panel:** Right-aligned drawer, 320px width, uses card sections with 16px padding.
- **Buttons:** Rounded corners (6px radius), primary buttons filled with Deep Blue and white text; secondary buttons outlined with 2px Deep Blue border.
- **Toasts:** Appear top-right, auto-dismiss after 5s, include icon and concise message.

## Accessibility
- Maintain minimum contrast ratio of 4.5:1 for text on backgrounds.
- Provide focus states with 2px outline using Primary action color at 60% opacity.
- Support keyboard navigation for all interactive controls.

## Content Guidelines
- Headlines: sentence case (e.g., "Create invoice").
- Button labels: imperative verbs ("Save", "Send invoice").
- Error messages: specify issue and action ("Email is required to create a client").

## Review & Maintenance
- Revisit guidelines quarterly or after major feature releases.
- Capture deviations in a design log and resolve within the next design cycle.
