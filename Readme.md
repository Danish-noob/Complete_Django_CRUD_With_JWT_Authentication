# Django REST API with JWT and Role-Based Authentication

This project is a Django application featuring a RESTful API secured with JWT (JSON Web Tokens) authentication. It implements role-based access control with two types of users:

- **Admin**: Can create and delete users and products.
- **User**: Can view products.

Currently, the app allows users to browse products, while admins manage users and products. More features will be added in the future.

---

## Features

- Django REST Framework API
- JWT authentication
- Role-based authorization (Admin and User roles)
- Admin CRUD operations on users and products
- User access to view products only

---


## Project Structure

```
db.sqlite3
manage.py
Role_Based_auth/           # Main Django project settings and URLs
Role_Based_auth_app/       # Main app: models, views, serializers, permissions, etc.
	 migrations/            # Database migrations
logs/                      # Log files
```

## Setup & Installation

1. Clone the repository and navigate to the project folder.
2. Create and activate a virtual environment:
	```powershell
	python -m venv venv
	.\venv\Scripts\activate
	```
3. Install dependencies:
	```powershell
	pip install -r requirements.txt
	```
4. Run migrations:
	```powershell
	python manage.py makemigrations
	python manage.py migrate
	```
5. (Optional) Seed demo data:
	```powershell
	python manage.py seed_demo
	```
6. Start the development server:
	```powershell
	python manage.py runserver
	```

## Demo Credentials

Demo user (created by `seed_demo`):
- Username: `owner`
- Password: `owner1234`

## API Usage (with Postman or similar)

1. Obtain JWT token:
	- POST `/api/auth/token/` with JSON body:
	  ```json
	  { "username": "owner", "password": "owner1234" }
	  ```
	- Copy the `access` token from the response.

2. Use the token for authenticated requests:
	- Add header: `Authorization: Bearer <access_token>`

3. Example endpoints:
	- List products: `GET /api/products/`
	- Create product: `POST /api/products/` (admin only)
	- List users: `GET /api/users/` (admin only)

## How It Works

- **Authentication**: Uses JWT (djangorestframework-simplejwt). Obtain a token, then use it for all protected endpoints.
- **Role-Based Access**: Permissions are enforced in views/permissions.py. Only users with the correct role can access certain endpoints.
- **Caching**: Uses Django's local memory cache for development (no Redis required).
- **Seeding Data**: `python manage.py seed_demo` creates a demo organization, user, category, and products.

## Troubleshooting

- If you see errors about missing columns, run migrations as shown above.
- If you see Redis connection errors, the project now uses local memory cache by default (no Redis needed).

---
## Future Plans

- Expand user functionality
- Add product reviews and ratings
- Implement order management
- Improve API documentation
