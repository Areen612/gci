# Customer Management Requirements

## User Stories

1. **View customer directory**  
   As a sales representative, I want to browse a paginated list of customers so that I can quickly scan and access the latest accounts.
2. **Search by name or company**  
   As a support agent, I want to search customers by person name, company name, or email so that I can respond to inbound requests without scrolling through the entire list.
3. **Filter by company**  
   As an account manager, I want to filter the customer list by company or status so that I can focus on a specific portfolio segment.
4. **Create a customer profile**  
   As a sales representative, I want to create a new customer profile with contact information so that the rest of the team can start working with the account immediately.
5. **Edit a customer profile**  
   As a sales representative, I want to update customer contact details so that everyone has the most current information.
6. **Delete a customer profile**  
   As an administrator, I want to delete an erroneous customer profile so that the directory stays clean and accurate.
7. **Archive a customer**  
   As a finance analyst, I want to archive customers that are no longer active so that historical records are preserved without appearing in the active list.
8. **Reactivate an archived customer**  
   As a sales lead, I want to reactivate a previously archived customer when business resumes so that the account can be managed again.

## Implementation Tasks

### Web Views and Forms

- Implement class-based or function-based views for customer list, detail, create, update, delete, archive, and reactivate endpoints.
- Build `ModelForm` classes for customer creation and updates, including inline formsets for related addresses and contact methods.
- Create the templates required for list, detail, form, delete confirmation, archive confirmation, and reactivate confirmation pages.
- Provide DRF serializers and viewsets/endpoints if an API layer is required for customer CRUD operations.

### Admin Customization

- Configure the Django admin list display to show customer name, company, status, primary email, and created date.
- Add list filters for customer status (active/archived) and company.
- Register inline admin sections for related addresses and contact methods on the customer admin page.
- Include search fields for name, company, and email within the admin interface.

### Search and Filtering

- Integrate `django-filter` for filtering customers by status, company, and created date in the list view.
- Add full-text search support with `SearchVector` on name, email, and company fields (with a fallback to `icontains` for non-Postgres setups).
- Ensure search and filter parameters are available via query string and preserved in pagination links.
- Expose search/filter capabilities through the API endpoints if DRF is used.

