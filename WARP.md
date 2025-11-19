# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repo Layout

- Root contains high-level docs and Python dependencies.
- The actual Django project lives in `django_ecommerce/`.
- Core Django pieces:
  - `django_ecommerce/manage.py` – entrypoint for all Django management commands.
  - `django_ecommerce/ecommerce_project/` – Django project config (`settings.py`, `urls.py`, `wsgi.py`).
  - `django_ecommerce/products/` – single main app (models, views, URLs, templates integration).
  - `django_ecommerce/templates/` & `django_ecommerce/static/` – global templates and static assets referenced by the `products` app.

When working with the app, assume `django_ecommerce/` is the project root unless stated otherwise.

## Common Commands

All commands below assume your shell is in `django_ecommerce/`.

### Environment & Dependencies

- Create and activate a virtualenv (Windows PowerShell):
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

- Install dependencies (from `requirements.txt`):
  ```bash
  pip install -r requirements.txt
  ```

### Database & Admin

- Create / update database schema:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

- Create an admin (superuser) account:
  ```bash
  python manage.py createsuperuser
  ```

### Running the App

- Run the Django development server locally:
  ```bash
  python manage.py runserver
  ```

- Local URLs of interest:
  - Storefront home page: `http://127.0.0.1:8000/`
  - Product list: `http://127.0.0.1:8000/products/`
  - Product detail: `http://127.0.0.1:8000/product/<product-slug>/`
  - Contact page: `http://127.0.0.1:8000/contact/`
  - Admin: `http://127.0.0.1:8000/admin/`

### Tests & Linting

- There is no dedicated test or lint tooling configured in this repo.
- If/when Django tests are added, standard commands are:
  - Run all tests:
    ```bash
    python manage.py test
    ```
  - Run tests for a single app / test case / test method (examples):
    ```bash
    python manage.py test products
    python manage.py test products.tests.ProductModelTests
    python manage.py test products.tests.ProductModelTests.test_discount_calculation
    ```

### Deployment

- There is a `Procfile` configured for a WSGI server:
  ```bash
  web: gunicorn ecommerce_project.wsgi --log-file -
  ```
- `ecommerce_project/settings.py` is preconfigured for deployment on Render:
  - `DEBUG = False` by default.
  - `ALLOWED_HOSTS` includes `localhost`, `127.0.0.1`, and `teaproject.onrender.com`.
  - If `RENDER_EXTERNAL_HOSTNAME` is set in the environment, it is appended to `ALLOWED_HOSTS`.

## High-Level Architecture

### Request Routing

- Project-level URLs: `ecommerce_project/urls.py`
  - Routes `/admin/` to Django admin.
  - Routes `/` (root) to `products.urls`, so the `products` app owns all public-facing URLs.
  - When `settings.DEBUG` is `True`, static and media files are served via `django.conf.urls.static` using `STATIC_URL`, `STATICFILES_DIRS`, and `MEDIA_URL`/`MEDIA_ROOT`.

- App-level URLs: `products/urls.py`
  - `/` → `home` view (storefront landing page).
  - `/products/` → `product_list` view.
  - `/product/<slug:slug>/` → `product_detail` view.
  - `/contact/` → `contact` view.

### Data Model Overview (`products/models.py`)

- **HomePage**
  - Stores editable content for the home page (title, subtitle, hero image, featured text, active flag).
  - `save()` enforces that only one `HomePage` instance can be active at a time (when a record is saved with `is_active=True`, all other active records are deactivated).
  - Used by the `home` view to render the landing page.

- **Category**
  - Basic product categorization (name, slug, optional description).
  - `slug` is unique and used for filtering in `product_list`.

- **Product**
  - Central e-commerce entity with:
    - Descriptions (`description`, `short_description`).
    - Pricing (`price`, optional `original_price` for discounts).
    - Material info (`material`).
    - Up to five images, with `primary_image` plus fallback image fields.
    - Foreign key to `Category` (nullable, `related_name='products'`).
    - Rating metadata (`rating`, `review_count`).
    - Stock information (`in_stock`, `stock_quantity`).
    - Free-form `features` and `specifications` fields (stored as text, parsed at runtime).
    - SEO fields (`meta_title`, `meta_description`).
  - Behavior:
    - `save()` auto-generates a slug from `name` when absent and guarantees slug uniqueness by adding a numeric suffix as needed.
    - `get_absolute_url()` returns the canonical product detail URL (used in templates).
    - `get_discount_percentage()` computes discount percentage from `original_price` and `price`.
    - `get_display_image()` selects the primary image, falling back to the first available secondary image.
    - `get_images()` returns all available images in display order.
    - `get_features_list()` returns a list of features parsed from `features` (newline or comma-separated).
    - `get_specifications_dict()` parses key:value pairs from `specifications` into a dictionary for template rendering.

- **OrderInquiry**
  - Lightweight model to represent a "contact to buy" flow instead of real payments.
  - Fields: associated `Product`, customer `name`, `email`, optional `phone`, `message`, and `created_at` timestamp.
  - `save()` triggers `send_notification_email()` on first save.
  - `send_notification_email()` builds an email body and sends it via Django's `send_mail` function to the store owner address.
    - Email destination is `settings.STORE_OWNER_EMAIL`.
    - Uses `EMAIL_BACKEND` from settings; by default this is the console backend, so emails appear in logs during development.

### Views & Templates (`products/views.py`)

- **home(request)**
  - Fetches the currently active `HomePage` instance (if any).
  - Builds a `featured_products` queryset ordered by `review_count`, `rating`, and `created_at` (top 8 products).
  - Loads up to six categories for quick navigation.
  - Renders `templates/products/home.html` with these objects.

- **product_list(request)**
  - Base queryset: all `Product` instances (with `select_related('category')`).
  - Supports multiple query parameters for filtering and sorting:
    - `in_stock=true` → restricts to products where `in_stock=True`.
    - `search` → text search across `name`, `description`, and `category__name` using `icontains` queries.
    - `category` → filter by category `slug`.
    - `max_price` → filter with `price__lte` (ignores invalid values).
    - `min_rating` → filter with `rating__gte` (ignores invalid values).
    - `sort` → one of:
      - `price-low`, `price-high`, `newest`, `rating`, `name-asc`, `name-desc`, or `bestsellers` (default).
  - Provides the current filters back to the template via context for building UI controls.
  - Renders `templates/products/product_list.html`.

- **product_detail(request, slug)**
  - Loads a single `Product` by `slug` or 404s.
  - GET: displays the product detail page.
  - POST: handles an inline inquiry form:
    - Validates that `name` and `email` are present.
    - Creates an `OrderInquiry` row, which in turn sends a notification email (via the model hook).
    - Exposes `success` / `error` flags to the template to drive user feedback.
  - Renders `templates/products/product_detail.html`.

- **contact(request)**
  - Generic contact form (not tied to a specific product).
  - On POST, validates that `name`, `email`, and `message` are filled; sets `success` or `error` accordingly.
  - Currently does not send email; it only toggles `success` for UI feedback.
  - Injects `store_owner_email` into the template, defaulting to the `STORE_OWNER_EMAIL` setting.
  - Renders `templates/contact.html`.

### Settings & Environment (`ecommerce_project/settings.py`)

- Base configuration:
  - SQLite database stored at `BASE_DIR / 'db.sqlite3'`.
  - `INSTALLED_APPS` includes standard Django contrib apps plus `products`.
  - Templates look in `BASE_DIR / 'templates'` as well as app template directories (`APP_DIRS=True`).

- Static & media files:
  - `STATIC_URL = '/static/'` with `STATICFILES_DIRS = [BASE_DIR / 'static']`.
  - `MEDIA_URL = '/media/'` and `MEDIA_ROOT = BASE_DIR / 'media'`.

- Email-related settings:
  - `STORE_OWNER_EMAIL` is read from env var `STORE_OWNER_EMAIL` and defaults to a concrete email address.
  - `DEFAULT_FROM_EMAIL` is set to `STORE_OWNER_EMAIL`.
  - `EMAIL_BACKEND` defaults to `django.core.mail.backends.console.EmailBackend` but can be overridden via an `EMAIL_BACKEND` environment variable.

## How This Relates to Existing Docs

Key points from existing documentation files (`README_DJANGO.md`, `QUICK_START.md`, `SETUP_COMPLETE.md`) are already reflected above:

- Use `django_ecommerce/` as the working directory for all Django commands.
- Setup flow is: install dependencies → run migrations → create superuser → run server.
- Home page content is fully editable via the **Home Page** model in admin.
- URL structure is:
  - `/` → configurable home page with featured products.
  - `/products/` → catalog with filtering, search, and sorting.
  - `/product/<product-slug>/` → product detail with inquiry form.
  - `/contact/` → general contact form.
  - `/admin/` → admin interface for managing `HomePage`, `Category`, `Product`, and `OrderInquiry` records.

Future modifications to models, views, or URL patterns should keep these high-level flows and conventions in mind so that the existing templates and docs remain accurate.