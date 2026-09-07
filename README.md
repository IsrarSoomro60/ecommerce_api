# Ecommerce API

A production-style e-commerce REST API built with Django REST Framework — featuring JWT authentication, role-based permissions, cart & checkout logic, order management, and a verified-purchase review system.

[![Django](https://img.shields.io/badge/Django-6.1-092E20?logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-REST%20Framework-red)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org/)

---

## Overview

This project goes beyond a basic CRUD app to demonstrate realistic e-commerce business logic: cart-to-order checkout with atomic transactions, stock management, price snapshotting for order history, role-based access control, and purchase-verified reviews.

## Features

- **Authentication** — JWT-based (access + refresh tokens), refresh token rotation & blacklisting, secure logout
- **Role-based permissions** — customer / admin / staff roles; admin-only product management; self-registration always defaults to `customer`
- **Products & Categories** — full CRUD, filtering, search, ordering, pagination
- **Cart** — add/update/remove items, automatic quantity merging, live total calculation
- **Orders** — cart-to-order checkout wrapped in a database transaction, automatic stock reduction, price/name snapshotting (so order history never changes even if products are later edited), stock validation before purchase
- **Order status management** — customers can cancel their own pending orders (with automatic stock restoration); admin/staff can set any order status and view all orders across all users
- **Reviews** — one review per user per product, restricted to users who have actually purchased the product, owner-only edit/delete
- **Consistent API responses** — every endpoint returns a standardized `{success, message, data}` / `{success, message, errors}` shape
- **Automated tests** — 32+ tests covering authentication, permissions, checkout logic, validation, and business rules
- **Interactive API docs** — Swagger UI and ReDoc, auto-generated from the codebase

## Tech Stack

- **Backend:** Django, Django REST Framework
- **Auth:** SimpleJWT (JWT access/refresh, rotation, blacklisting)
- **Filtering:** django-filter
- **Docs:** drf-spectacular (OpenAPI/Swagger)
- **Config:** python-dotenv
- **Database:** SQLite (dev) — PostgreSQL (planned for production)

## Project Structure

```
ecommerce_api/
├── config/         # project settings & root URLs
├── core/           # shared utilities: exception handler, response helpers, permissions
├── users/          # custom User model, auth (register/login/logout), roles
├── products/       # Product & Category models, CRUD API
├── cart/           # Cart & CartItem models, add/update/remove logic
├── orders/         # Order & OrderItem models, checkout, status transitions
└── reviews/        # Review model, purchase-verified review system
```

## Setup Instructions

1. **Clone the repo, then navigate into it**
   ```bash
   cd ecommerce_api
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv myenv
   # Windows
   myenv\Scripts\activate
   # Mac/Linux
   source myenv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser** (for admin panel access)
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the server**
   ```bash
   python manage.py runserver
   ```

8. **Run the test suite**
   ```bash
   python manage.py test
   ```

## API Documentation

Once the server is running, explore the full interactive API docs at:

- **Swagger UI:** `http://127.0.0.1:8000/api/docs/`
- **ReDoc:** `http://127.0.0.1:8000/api/redoc/`
- **Django Admin:** `http://127.0.0.1:8000/admin/`

## Key Endpoints

| Endpoint | Description |
|---|---|
| `POST /api/users/register/` | Register a new user (always created as `customer`) |
| `POST /api/users/login/` | Obtain JWT access + refresh tokens |
| `POST /api/users/login/refresh/` | Refresh an access token |
| `POST /api/users/logout/` | Blacklist a refresh token |
| `GET /api/users/me/` | Get the authenticated user's profile |
| `GET/POST /api/products/` | List / create products |
| `GET/POST /api/categories/` | List / create categories |
| `GET /api/cart/` | View the current user's cart |
| `POST /api/cart/add/` | Add a product to the cart |
| `POST /api/orders/checkout/` | Convert the cart into an order |
| `GET /api/orders/` | List orders (own orders, or all orders for admin/staff) |
| `PATCH /api/orders/<id>/status/` | Update an order's status |
| `GET/POST /api/reviews/` | List / create product reviews |

## Design Decisions

- **Price snapshotting on orders** — `OrderItem` stores `product_name` and `price` at the time of purchase, so historical orders remain accurate even if a product is later renamed, repriced, or removed.
- **Atomic checkout** — order creation, stock reduction, and cart clearing all happen inside a single database transaction, so a failure partway through never leaves inconsistent data.
- **PROTECT over CASCADE** — categories and ordered products can't be deleted while still referenced, preventing accidental data loss.
- **Purchase-verified reviews** — review eligibility is checked against real `OrderItem` history rather than trusted client input.
- **Scope discipline** — deliberately avoided adding Kafka, Kubernetes, microservices, Redis, Celery, or RabbitMQ, since none of them solve an actual problem in this project's scope.

## Roadmap

- [ ] PostgreSQL migration
- [ ] Docker + Gunicorn + Nginx deployment
- [ ] LLM-based semantic product search/recommendation

## Author

**Israr Ahmed**
- LinkedIn: [israrahmedsoomro](https://linkedin.com/in/israrahmedsoomro)
- Portfolio: [israr151.netlify.app](https://israr151.netlify.app)
