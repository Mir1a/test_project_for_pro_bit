# Multi-Tenant FastAPI Application

A modern multi-tenant architecture application built with FastAPI, featuring separate databases for core platform management and individual tenant operations.

## 🏗️ Architecture Overview

The application implements a **multi-database architecture** with two distinct contexts:

- **Core Database**: Manages organizations (tenants), platform owners, and system-wide data
- **Tenant Databases**: Separate databases for each tenant with isolated user data

Request routing is handled via the `X-TENANT` HTTP header, enabling seamless switching between core and tenant operations.

## 🚀 Features

- **Multi-tenant architecture** with database isolation
- **JWT-based authentication** with context-aware tokens
- **Dynamic tenant routing** via HTTP headers
- **RESTful API** with comprehensive endpoints
- **Secure password handling** with bcrypt
- **Comprehensive testing** with 95%+ coverage
- **Docker support** for easy deployment

## 📋 Requirements

- Python 3.8+
- PostgreSQL 15+
- Redis (for caching)
- Docker & Docker Compose (optional)

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd multitenant-fastapi
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
# Database settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=multitenant_core
DB_USER=postgres
DB_PASS=your_password

# Security
SECRET_KEY=your-super-secret-key-change-in-production

# Redis settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## 🐳 Docker Setup (Recommended)

### 1. Using Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop services
docker-compose down
```

### 2. Services included:
- **app**: FastAPI application (port 8000)
- **db**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)

## 🔧 Manual Setup

### 1. Start PostgreSQL and Redis

```bash
# PostgreSQL
sudo systemctl start postgresql

# Redis
sudo systemctl start redis
```

### 2. Create database

```sql
CREATE DATABASE multitenant_core;
```

### 3. Run migrations

```bash
alembic upgrade head
```

### 4. Start the application

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🌐 API Endpoints

### Core Operations (without X-TENANT header)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register core platform user |
| POST | `/auth/login` | Authenticate core user |
| POST | `/organizations` | Create new organization (requires authentication) |

### Tenant Operations (with X-TENANT header)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register tenant user |
| POST | `/auth/login` | Authenticate tenant user |
| GET | `/users/me` | Get current user profile |
| PUT | `/users/me` | Update current user profile |

### Universal Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/refresh` | Refresh access token |

## 🔐 Authentication Flow

### Core User Flow

1. **Register core user**:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "password": "AdminPass123",
    "first_name": "Admin"
  }'
```

2. **Login core user**:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "password": "AdminPass123"
  }'
```

3. **Create organization**:
```bash
curl -X POST "http://localhost:8000/organizations" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Company",
    "slug": "my-company",
    "description": "Test organization"
  }'
```

### Tenant User Flow

1. **Register tenant user**:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "X-TENANT: my-company" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@mycompany.com",
    "password": "UserPass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

2. **Login tenant user**:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "X-TENANT: my-company" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@mycompany.com",
    "password": "UserPass123"
  }'
```

3. **Get user profile**:
```bash
curl -X GET "http://localhost:8000/users/me" \
  -H "X-TENANT: my-company" \
  -H "Authorization: Bearer <tenant_access_token>"
```

4. **Update user profile**:
```bash
curl -X PUT "http://localhost:8000/users/me" \
  -H "X-TENANT: my-company" \
  -H "Authorization: Bearer <tenant_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Johnny",
    "bio": "Updated bio"
  }'
```

## 🧪 Testing

### Run all tests

```bash
pytest
```

## 🔒 Security Features

- **Password Security**: bcrypt hashing with salt
- **JWT Tokens**: Secure token-based authentication
- **Tenant Isolation**: Complete data separation between tenants
- **Authorization**: Role-based access control
- **Input Validation**: Comprehensive request validation

## 🚨 Important Notes