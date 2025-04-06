# Recall Backend

A Django REST API backend for the Recall search engine application. This backend provides authentication, user management, subscription management, and search functionality.

## Features

- Custom user authentication system with individual, company, and employee user types
- Session-based authentication
- OTP verification for registration
- Subscription management with Stripe integration
- Search functionality
- PostgreSQL database integration
- Docker support for development and production
- CORS configuration for frontend integration

## Tech Stack

- Python 3 with Django 5.1.7
- Django REST Framework for API endpoints
- PostgreSQL for database (SQLite option for local development)
- Redis for caching
- Stripe for payment processing
- Docker and Docker Compose for containerization

## Development Setup

### Option 1: Using Docker (PostgreSQL)

1. Clone the repository:
```bash
git clone https://github.com/Hassant147/recall-backend.git
cd recall-backend
```

2. Copy the example environment file:
```bash
cp .env.example .env
```

3. Update the environment variables in the `.env` file with your values

4. Start the development server with Docker:
```bash
docker-compose up
```

### Option 2: Local Development with SQLite

For quick local development without needing to set up PostgreSQL:

1. Clone the repository:
```bash
git clone https://github.com/Hassant147/recall-backend.git
cd recall-backend
```

2. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a local environment file:
```bash
cp .env.example .env.local
```

5. Edit `.env.local` and set:
```
DEBUG=True
IS_PRODUCTION=False
```

6. Run migrations and start the server:
```bash
python manage.py migrate
python manage.py runserver
```

The system will automatically use SQLite for local development when `DEBUG=True` and `IS_PRODUCTION=False`.

## API Documentation

See [api_documentation.md](api_documentation.md) for detailed API endpoints and usage.

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions.

## Frontend Guide

See [frontend_guide.md](frontend_guide.md) for instructions on integrating with the frontend. 