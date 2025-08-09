# Enterprise Job Board API (FastAPI, Clean Architecture)

A production-ready backend for a Job Board platform built with FastAPI, Pydantic, and SQLAlchemy, following Clean Architecture and SOLID principles. Includes JWT auth, RBAC-ready structure, Docker/Compose, and testing.

## 🎯 Overview

- Purpose: Manage users, jobs, and applications with clear layering and testability.
- Principles: Clean Architecture, SOLID, Repository/Service patterns, high cohesion, low coupling.
- Status: API v1 stable; suitable as a foundation for enterprise deployments.

## 🏗 Architecture

### Layered Architecture

```mermaid
graph TD
  A["Clients"] --> B["Interfaces: FastAPI Routers"]
  B --> C["Application: Services, Schemas, Use-Cases"]
  C --> D["Domain: Entities, Rules"]
  C --> E["Infrastructure: Repositories, DB, Integrations"]
  E --> F["PostgreSQL"]
  E --> G["Redis"]
```

- Interfaces: `app/interfaces/api/v1` (routers, request mapping)
- Application: `app/application` (services, schemas, orchestration)
- Domain: `app/domain` (entities + business rules)
- Infrastructure: `app/infrastructure` (ORM models, repositories, DB config)

### Request Lifecycle

```mermaid
sequenceDiagram
  participant C as "Client"
  participant R as "FastAPI Router"
  participant S as "Service (Application)"
  participant Repo as "Repository (Infrastructure)"
  participant DB as "PostgreSQL"

  C->>R: HTTPS /api/v1/... (JWT optional)
  R->>S: Validate via Pydantic Schemas
  S->>Repo: Execute use-case
  Repo->>DB: SQLAlchemy CRUD
  DB-->>Repo: Rows
  Repo-->>S: Domain objects/DTO
  S-->>R: Response model
  R-->>C: JSON response
```

### Data Model (High-level)

```mermaid
erDiagram
  USERS ||--o{ JOBS : "created_by"
  USERS ||--o{ APPLICATIONS : "applicant"
  JOBS ||--o{ APPLICATIONS : "applied_to"

  USERS {
    uuid id PK
    string full_name
    string email
    string hashed_password
    enum role
    boolean is_active
    boolean is_verified
    timestamp created_at
    timestamp updated_at
  }

  JOBS {
    uuid id PK
    string title
    string description
    string location
    enum status
    uuid created_by FK
    timestamp created_at
    timestamp updated_at
  }

  APPLICATIONS {
    uuid id PK
    uuid applicant_id FK
    uuid job_id FK
    string resume_link
    text cover_letter
    enum status
    timestamp applied_at
    timestamp updated_at
  }
```

### Deployment Topology

```mermaid
graph LR
  User["End Users"] -->|"HTTPS"| CDN["CDN / WAF"]
  CDN --> API["FastAPI App (Containers)"]
  API -->|"SQLAlchemy"| PG["Managed PostgreSQL"]
  API -->|"Cache/Queues (optional)"| REDIS["Managed Redis"]
  API -->|"Observability"| Sentry["Sentry / APM"]
```

## 📁 Repository Structure

```
app/
  core/                # config, security, exceptions, interfaces
  domain/              # entities and domain rules
  application/         # services and schemas
  infrastructure/      # DB, models, repositories
  interfaces/          # FastAPI routers and API
  main.py              # app factory and middleware
Dockerfile
docker-compose.yml
requirements.txt
tests/
```

## 🛠 Technology Stack

- Framework: FastAPI 0.104.1 on Starlette
- Language: Python 3.11+ (tested with 3.12)
- ORM: SQLAlchemy 2.0.x
- Validation: Pydantic 2.x
- Auth: JWT (python-jose), bcrypt hashing
- Runtime: Uvicorn
- DevOps: Docker, docker-compose
- Quality: black, isort, flake8, mypy, pytest, coverage
- Optional: Redis cache/queues, Sentry

## ⚙️ Environment Variables (Production)

Configure via your cloud provider’s environment settings (do not commit secrets):

```env
# Application
APP_NAME=Enterprise Backend
APP_VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Database (PostgreSQL)
# Recommended (managed DB, SSL required on most providers):
DATABASE_URL=postgresql://<db_user>:<db_password>@<db_host>:<db_port>/<db_name>?sslmode=require
DATABASE_ECHO=false

# Redis (optional)
REDIS_URL=redis://<redis_host>:<redis_port>

# Security
SECRET_KEY=<generate-a-strong-random-secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
PUBLIC_BASE_URL=https://api.<your-domain>

# CORS
ALLOWED_ORIGINS=["https://app.<your-domain>", "https://<another-origin>"]

# Email (optional)
SMTP_HOST=<smtp_host>
SMTP_PORT=<smtp_port>
SMTP_USER=<smtp_username>
SMTP_PASSWORD=<smtp_password>
SMTP_USE_TLS=true
FROM_EMAIL=no-reply@<your-domain>

# Observability (optional)
SENTRY_DSN=<sentry_dsn>
LOG_LEVEL=INFO
```

## 🚀 Production Deployment

- Container image runs Uvicorn on port 8000 (exposed by Dockerfile).
- Health check path: `/health`.
- Ensure `DATABASE_URL` points to your managed Postgres host (not localhost). For internal VPC endpoints, you may omit `sslmode=require`; for public endpoints, add `?sslmode=require`.
- Set `PUBLIC_BASE_URL` to your API domain (e.g., `https://api.<your-domain>`).
- Set `ALLOWED_ORIGINS` to your frontend origins.

### Example: Docker Compose (production-like)

```yaml
services:
  app:
    image: <your-registry>/<your-app>:<tag>
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
      - PUBLIC_BASE_URL=https://api.<your-domain>
      - ALLOWED_ORIGINS=["https://app.<your-domain>"]
    depends_on:
      - db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 30s
      retries: 3
      start_period: 5s

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=<db_name>
      - POSTGRES_USER=<db_user>
      - POSTGRES_PASSWORD=<db_password>
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U <db_user> -d <db_name>"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### Example: Cloud (Render/Heroku/Railway)

- Create a managed Postgres instance.
- Set environment variables in your web service:
  - `DATABASE_URL=postgresql://<db_user>:<db_password>@<db_host>:<db_port>/<db_name>?sslmode=require`
  - `SECRET_KEY=<strong-secret>`
  - `PUBLIC_BASE_URL=https://api.<your-domain>`
  - `ALLOWED_ORIGINS=["https://app.<your-domain>"]`
- Deploy. The app will wait for the DB during startup and create tables automatically.

## 🔐 Security

- JWT-based auth with configurable expiry and algorithm
- Bcrypt password hashing
- CORS policy via settings
- Trusted hosts middleware
- Centralized exception handlers
- Secrets via environment variables or secret manager

## 📚 API Notes

- Base path: `/api/v1`
- API Docs (production): `https://api.<your-domain>/docs`
- ReDoc (production): `https://api.<your-domain>/redoc`
- Health: `https://api.<your-domain>/health`
- Authorization header: `Authorization: Bearer <token>`

## 🧪 Testing

```bash
pytest -q
pytest --cov=app
pytest tests/test_users.py -vv
```

## 🧹 Code Quality

```bash
black app/
isort app/
flake8 app/
mypy app/
```

## 🗄 Database

- Primary database: Managed PostgreSQL.
- SQLAlchemy engine configured in `app/infrastructure/database/base.py` with pool pre-ping and startup retry.
- For production, manage schema with Alembic migrations.

### Migrations (Alembic)

```bash
alembic init migrations
# Configure sqlalchemy.url in alembic.ini to your DATABASE_URL
alembic revision -m "init"
alembic upgrade head
```

## 📦 Observability & Ops

- Logging via `LOG_LEVEL` (extend with `structlog` if desired)
- Optional Sentry via `SENTRY_DSN`
- Add metrics endpoints or Prometheus client as needed
- Consider rate limiting, WAF, and request size limits

## 🤝 Contributing

1. Fork & clone
2. Create a feature branch
3. Add tests and ensure `pytest` passes
4. Run formatters and linters
5. Open a Pull Request

## 📝 License

MIT (or your chosen license)
