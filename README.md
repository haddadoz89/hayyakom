Hayyakom - Investment Crowdfunding Platform
A full-stack crowdfunding platform built with Django, designed to connect small and medium-sized business owners in Bahrain with a network of local investors. Hayyakom facilitates the entire funding lifecycle, from campaign creation and admin approval to secure online payments and post-funding progress tracking.

✨ Features
Role-Based User System: Separate, tailored experiences for Business Owners and Investors.

Secure Authentication: Full user signup, login/logout, profile management, and password reset functionality.

Admin Approval Workflow: A secure process where administrators must approve new campaigns before they are visible to the public.

Secure Payments: Integration with the Stripe payment gateway for handling real financial transactions in a test environment.

Dynamic Dashboards: Personalized dashboards for both owners and investors to manage their activities.

Interactive Roadmaps: A unique post-funding feature where owners can add and complete milestones, which automatically notifies investors.

The Investor Passport: A "trophy case" feature that displays a digital stamp for every successfully funded campaign an investor has backed.

Automated Lifecycle Management: A daily script automatically updates the status of campaigns that have reached their end date.

In-App Notifications: A notification system to keep users informed of key events like new investments, campaign approvals, and milestone completions.

Search & Filtering: Powerful search and category filtering on public campaign lists.

🧱 Tech Stack
Backend: Django, PostgreSQL

Payments: Stripe

Environment Variables: python-decouple, python-dotenv

Database Driver: psycopg2-binary

Frontend: HTML, CSS (with a mobile-first responsive design), JavaScript

JavaScript Libraries: flatpickr (for date selection)

🗂️ Repository Structure
hayyakom_project/
├── .env              # Local environment variables (must be created)
├── hayyakom/         # Django project configuration files (settings.py, urls.py)
├── main_app/         # The core application logic, models, views, and templates
├── manage.py         # Django's command-line utility
└── requirements.txt  # A list of all Python package dependencies

🖥️ URL & Page Overview
/ (Home Page): A public, searchable, and filterable list of all active and approved campaigns.

/accounts/signup/: New user registration form with role selection (Owner or Investor).

/accounts/login/: User login page.

/fundings/ (Dashboard): A protected, personalized dashboard.

For Owners: Shows their company profile and a link to manage their campaigns.

For Investors: Shows a table of their personal investments and their status.

/fundings/<id>/ (Campaign Detail): A detailed view of a single campaign, showing its description, funding progress, and the interactive roadmap.

/company/<id>/ (Company Detail): A public profile for a company, showing its details and a list of all its campaigns.

/profile/: A private page for a logged-in user to update their personal information.

/passport/: An investor's private "trophy case" of successfully backed campaigns.

/admin/: The powerful, customized Django Admin panel for site administrators to manage users and approve campaigns.

🚀 Getting Started
To get a local copy up and running, follow these steps.

Prerequisites
Python 3.10+

PostgreSQL

Installation & Setup
Clone the repository:

git clone <your-repo-url>
cd hayyakom_project

Create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate

Install all dependencies:

pip install -r requirements.txt

Set up the .env file:
Create a new file named .env in the project root and add your secret keys.

SECRET_KEY=your_django_secret_key
DEBUG=True
DATABASE_NAME=hayyakomdb
DATABASE_USER=your_postgres_username
DATABASE_PASSWORD=your_postgres_password
DATABASE_PORT=5432
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

Set up the PostgreSQL Database:
Make sure PostgreSQL is running and create the database.

createdb hayyakomdb

Run the Database Migrations:

python manage.py migrate

Create an Admin Superuser:

python manage.py createsuperuser

Run the Development Server:

python manage.py runserver

Future Enhancements
"Lead Investor" Syndicates: Allow reputable investors to publicly back and lead investment rounds to increase trust.

The "Hayyakom Guild": A private marketplace connecting funded businesses with skilled investors offering professional services.

Terms of Service & Public Q&A: Add legal pages and a public Q&A section on campaign pages to increase transparency.