# Coderr Backend

A Django REST Framework backend for **Coderr**, a marketplace platform where business users publish service offers and customer users place orders and write reviews.

---

## Features

- Token-based authentication (DRF `authtoken`)
- User registration & login (customer / business)
- User profiles with type-specific list endpoints
- Offers with three pricing tiers (basic / standard / premium)
- Orders created from offer details, status-tracked by business users
- Reviews (one per customer per business, filterable & orderable)
- Public base-info endpoint for landing-page statistics
- Guest login management command for frontend demos
- Pagination (page size = 6), filtering via `django-filter`, ordering
- 63 automated tests (`APITestCase`)

---

## Tech Stack

- Python 3.13
- Django 6.0
- Django REST Framework 3.17
- django-filter 25.2
- SQLite (development)

---

## Installation

### 1. Clone

```powershell
git clone <repo-url>
cd coderr-backend
```

### 2. Create & activate a virtual environment

```powershell
python -m venv env
env\Scripts\activate
```

On macOS / Linux:

```bash
python -m venv env
source env/bin/activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run migrations

```powershell
python manage.py migrate
```

### 5. (Optional) Create a superuser

```powershell
python manage.py createsuperuser
```

### 6. Create guest users (for frontend demo login)

```powershell
python manage.py create_guest_users
```

This creates two accounts:

| Username   | Password | Type     |
| ---------- | -------- | -------- |
| `customer` | `123456` | customer |
| `business` | `123456` | business |

### 7. Start the development server

```powershell
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/`.

---

## Running Tests

```powershell
python manage.py test
```

All 63 tests should pass.

---

## API Overview

All endpoints are prefixed with `/api/`.

### Authentication

| Method | Endpoint         | Description                          |
| ------ | ---------------- | ------------------------------------ |
| POST   | `/registration/` | Register a new user (customer/business) |
| POST   | `/login/`        | Obtain auth token                    |

Include the returned token in subsequent requests:

```
Authorization: Token <your-token>
```

### Profiles

| Method       | Endpoint                  | Description                         |
| ------------ | ------------------------- | ----------------------------------- |
| GET / PATCH  | `/profile/<pk>/`          | Retrieve / update own profile       |
| GET          | `/profiles/business/`     | List all business profiles          |
| GET          | `/profiles/customer/`     | List all customer profiles          |

### Offers

| Method                | Endpoint              | Description                          |
| --------------------- | --------------------- | ------------------------------------ |
| GET / POST            | `/offers/`            | List / create offers (business only) |
| GET / PATCH / DELETE  | `/offers/<pk>/`       | Retrieve / update / delete an offer  |
| GET                   | `/offerdetails/<pk>/` | Retrieve a single offer detail       |

### Orders

| Method                | Endpoint                              | Description                              |
| --------------------- | ------------------------------------- | ---------------------------------------- |
| GET / POST            | `/orders/`                            | List / create orders (customer creates)  |
| GET / PATCH / DELETE  | `/orders/<pk>/`                       | Retrieve / update status / delete        |
| GET                   | `/order-count/<business_user_id>/`    | Count of in-progress orders              |
| GET                   | `/completed-order-count/<business_user_id>/` | Count of completed orders        |

### Reviews

| Method                | Endpoint          | Description                                     |
| --------------------- | ----------------- | ----------------------------------------------- |
| GET / POST            | `/reviews/`       | List / create reviews (customer only)           |
| GET / PATCH / DELETE  | `/reviews/<pk>/`  | Retrieve / update / delete (reviewer only)      |

Query params: `?business_user_id=`, `?reviewer_id=`, `?ordering=rating|updated_at`.

### Base Info (public)

| Method | Endpoint       | Description                                                    |
| ------ | -------------- | -------------------------------------------------------------- |
| GET    | `/base-info/`  | `review_count`, `average_rating`, `business_profile_count`, `offer_count` |

---

## Project Structure

```
coderr-backend/
├── core/                 # Project settings, root URLs, pagination, base-info view
├── users_app/            # Registration & login
├── profiles_app/         # UserProfile model & profile endpoints
├── offers_app/           # Offer & OfferDetail
├── orders_app/           # Order model & endpoints
├── reviews_app/          # Review model & endpoints
├── tests/                # APITestCase suites (one file per app)
├── manage.py
└── requirements.txt
```

Each app follows the same layout:

```
<app>/
├── models.py
├── admin.py
└── api/
    ├── serializers.py
    ├── views.py
    ├── permissions.py
    └── urls.py
```

---

## Permissions Summary

| Action                          | Required                                  |
| ------------------------------- | ----------------------------------------- |
| Create offer                    | Authenticated business user               |
| Update / delete offer           | Offer owner                               |
| Create order                    | Authenticated customer user               |
| Update order status (PATCH)     | Business user of that order               |
| Delete order                    | Admin (staff) only                        |
| Create review                   | Authenticated customer user               |
| Update / delete review          | Reviewer (creator) only                   |
| View base-info                  | Public (no auth required)                 |

---

## License

Portfolio project — for educational purposes.
