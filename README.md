# GCI Design Documentation

This repository captures foundational design artifacts for the GCI invoicing experience and a working Django prototype for inventory operations.

## Contents
- `docs/wireframes.md` — low-fidelity wireframes for customer search, invoice list, and item editor screens.
- `docs/user_flows.md` — step-by-step flows for searching clients, adding clients, and creating invoices.
- `docs/usability_validation.md` — validation plan and findings from business-owner feedback sessions.
- `docs/ui_guidelines.md` — visual and content guidelines to maintain consistency across screens.
- `store/` — Django project implementing inventory item CRUD, stock adjustments, and admin tooling for managing catalogue data.

## Running the prototype

1. Install dependencies:

   ```bash
   pip install "Django>=4.2,<5.0"
   ```

2. Apply migrations and create a superuser:

   ```bash
   cd store
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. Start the development server:

   ```bash
   python manage.py runserver
   ```

The inventory module is available at `/inventory/` and provides search, filtering, CRUD actions, and stock adjustment workflows. The Django admin includes low-stock filters, inline adjustment history, and bulk activation controls.

Use these artifacts to guide future high-fidelity design and development work.
