# EventFlow API

EventFlow API is an asynchronous event booking service built with FastAPI, PostgreSQL, and SQLAlchemy. It supports event management, seat reservations, role-based access control, and JWT authentication with access and refresh tokens.

## Features

- User registration and authentication
- Password hashing with bcrypt
- JWT access and refresh tokens
- Role-based access for `customer`, `manager`, and `admin`
- Event creation and management
- Seat availability tracking
- Booking price calculation
- Controlled booking status transitions
- Soft deletion of events
- Asynchronous PostgreSQL queries
- Database migrations with Alembic

## Technology Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- AsyncPG
- Alembic
- Pydantic
- PyJWT
- Passlib and bcrypt

## Project Structure

```text
app/
├── migrations/       # Alembic migrations
├── models/           # SQLAlchemy models
├── routers/          # API endpoints
├── schemas/          # Pydantic schemas
├── auth.py           # Password hashing and token generation
├── config.py         # Environment configuration
├── database.py       # Async database connection
├── dependency.py     # Authentication and role dependencies
└── main.py           # FastAPI application
```

## Installation

```bash
git clone https://github.com/dnndjowow/eventflow-api.git
cd eventflow-api

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

## PostgreSQL Setup

```sql
CREATE USER eventflow_user WITH PASSWORD 'your_password';
CREATE DATABASE eventflow_db OWNER eventflow_user ENCODING 'UTF8';
```

## Environment Variables

Create `.env` from the provided example:

```bash
cp .env.example .env
```

Configure the following values:

```env
DATABASE_URL=postgresql+asyncpg://eventflow_user:your_password@localhost:5432/eventflow_db
SECRET_KEY=replace_with_a_secure_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Database Migrations

```bash
alembic upgrade head
```

## Running the Application

```bash
uvicorn app.main:app --reload
```

API documentation:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/auth/register` | Public | Register a customer |
| POST | `/auth/token` | Public | Receive access and refresh tokens |
| POST | `/auth/token/access` | Refresh token | Generate a new access token |
| GET | `/auth/me` | Authenticated | Get the current user |
| POST | `/events/` | Admin, Manager | Create an event |
| GET | `/events/` | Authenticated | Get active events |
| GET | `/events/{event_id}` | Authenticated | Get an event |
| PATCH | `/events/{event_id}` | Admin, Manager | Update an event |
| DELETE | `/events/{event_id}` | Admin | Deactivate an event |
| POST | `/bookings/` | Authenticated | Create a booking |
| GET | `/bookings/me` | Authenticated | Get personal bookings |
| GET | `/bookings/` | Admin, Manager | Get all bookings |
| GET | `/bookings/{booking_id}` | Owner, Admin, Manager | Get a booking |
| PATCH | `/bookings/{booking_id}/status` | Owner or staff | Change booking status |

## Business Rules

- Bookings can only be created before the booking deadline.
- The requested number of seats must be available.
- A user cannot have multiple active bookings for the same event.
- Booking price is saved when the booking is created.
- Cancelling a booking restores the reserved seats.
- Customers can only cancel their own active bookings.
- Staff members manage booking status transitions.
- Supported transitions are:
  `pending → confirmed → checked_in → completed`
- `pending` and `confirmed` bookings can also be cancelled.
- Events with active bookings cannot be deactivated.
- Event capacity cannot be reduced below the number of reserved seats.

## Roles

Newly registered users receive the `customer` role. For local development, an administrator can be assigned directly in PostgreSQL:

```sql
UPDATE users
SET role = 'admin'
WHERE username = 'your_username';
```

## Author

Created by [dnndjowow](https://github.com/dnndjowow).