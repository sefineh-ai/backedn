# Job Board API

A comprehensive RESTful API for job board management built with FastAPI, following enterprise-level design patterns, SOLID principles, and clean architecture.

## 🎯 Project Overview

This API enables companies to post and manage job listings while allowing applicants to browse jobs, submit applications, and track their application status. The system implements role-based access control, authentication, authorization, and comprehensive business logic.

## 🏗️ Architecture

### Clean Architecture Layers

1. **Domain Layer** (`app/domain/`)
   - Entities: `User`, `Job`, `Application`
   - Value objects and domain logic
   - Business rules and validations

2. **Application Layer** (`app/application/`)
   - Services: Business logic orchestration
   - Schemas: Request/response models
   - Use cases and application logic

3. **Infrastructure Layer** (`app/infrastructure/`)
   - Database models and repositories
   - External service integrations
   - Data persistence implementations

4. **Interface Layer** (`app/interfaces/`)
   - API endpoints and controllers
   - Authentication and authorization
   - Request/response handling

### Design Patterns Implemented

- **Repository Pattern**: Data access abstraction
- **Service Pattern**: Business logic encapsulation
- **Factory Pattern**: Object creation
- **Strategy Pattern**: Algorithm selection
- **Observer Pattern**: Event handling
- **Singleton Pattern**: Database manager
- **Dependency Injection**: Service composition

### SOLID Principles

- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes are substitutable
- **Interface Segregation**: Client-specific interfaces
- **Dependency Inversion**: High-level modules don't depend on low-level modules

## 🚀 Features

### User Management
- ✅ User registration (Company/Applicant roles)
- ✅ Email verification (token-based)
- ✅ User authentication (JWT)
- ✅ Password hashing (bcrypt)
- ✅ Role-based access control

### Job Management
- ✅ Create jobs (Company only)
- ✅ Update/delete jobs (Owner only)
- ✅ Job status management (Draft → Open → Closed)
- ✅ Job search and filtering
- ✅ Pagination support

### Application Management
- ✅ Submit applications (Applicant only)
- ✅ Track application status
- ✅ Update application status (Company only)
- ✅ Application filtering and sorting
- ✅ Resume upload support (Cloudinary)

### Security Features
- ✅ JWT authentication
- ✅ Password hashing with bcrypt
- ✅ Role-based authorization
- ✅ Input validation and sanitization
- ✅ Error handling and logging

## 🛠️ Technology Stack

- **Framework**: FastAPI 0.104.1
- **Language**: Python 3.12+
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy 2.0.23
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Validation**: Pydantic 2.5.0
- **Testing**: pytest, pytest-asyncio
- **Code Quality**: Black, isort, flake8, mypy
- **Documentation**: Swagger/OpenAPI

## 📋 Prerequisites

- Python 3.12+
- pip (Python package manager)
- Git

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd job-board-api
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
# Application
APP_NAME=Job Board API
APP_VERSION=1.0.0
DEBUG=true

# Database
DATABASE_URL=sqlite:///./job_board.db
DATABASE_ECHO=false

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Email (for production)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Cloudinary (for file uploads)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### 5. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 API Documentation

### Authentication

All protected endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### User Endpoints

#### 1. User Registration
```http
POST /api/v1/users/signup
Content-Type: application/json

{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "role": "applicant"
}
```

#### 2. User Login
```http
POST /api/v1/users/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

#### 3. Get User Profile
```http
GET /api/v1/users/{user_id}
Authorization: Bearer <token>
```

### Job Endpoints

#### 1. Create Job (Company Only)
```http
POST /api/v1/jobs/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Senior Python Developer",
  "description": "We are looking for an experienced Python developer...",
  "location": "Remote",
  "status": "Open"
}
```

#### 2. Get Jobs (with filters)
```http
GET /api/v1/jobs/?title=python&location=remote&page_number=1&page_size=10
```

#### 3. Get Job Details
```http
GET /api/v1/jobs/{job_id}
```

#### 4. Update Job (Owner Only)
```http
PUT /api/v1/jobs/{job_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Job Title",
  "status": "Closed"
}
```

### Application Endpoints

#### 1. Submit Application (Applicant Only)
```http
POST /api/v1/applications/
Authorization: Bearer <token>
Content-Type: application/json

{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "resume_link": "https://cloudinary.com/resume.pdf",
  "cover_letter": "I am excited to apply for this position..."
}
```

#### 2. Get My Applications (Applicant Only)
```http
GET /api/v1/applications/my-applications?page_number=1&page_size=10
Authorization: Bearer <token>
```

#### 3. Get Job Applications (Company Only)
```http
GET /api/v1/applications/job/{job_id}?page_number=1&page_size=10
Authorization: Bearer <token>
```

#### 4. Update Application Status (Company Only)
```http
PUT /api/v1/applications/{application_id}/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "Interview"
}
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_users.py

# Run with verbose output
pytest -v
```

### Test Structure

```
tests/
├── __init__.py
├── test_users.py
├── test_jobs.py
├── test_applications.py
└── conftest.py
```

## 🔧 Development

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

## 📊 Database Schema

### Users Table
- `id` (UUID, Primary Key)
- `full_name` (String, Required)
- `email` (String, Unique, Required)
- `hashed_password` (String)
- `role` (Enum: applicant/company)
- `is_active` (Boolean)
- `is_verified` (Boolean)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Jobs Table
- `id` (UUID, Primary Key)
- `title` (String, Required)
- `description` (String, Required)
- `location` (String, Optional)
- `status` (Enum: Draft/Open/Closed)
- `created_by` (UUID, Foreign Key)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Applications Table
- `id` (UUID, Primary Key)
- `applicant_id` (UUID, Foreign Key)
- `job_id` (UUID, Foreign Key)
- `resume_link` (String, Required)
- `cover_letter` (Text, Optional)
- `status` (Enum: Applied/Reviewed/Interview/Rejected/Hired)
- `applied_at` (DateTime)
- `updated_at` (DateTime)

## 🚀 Deployment

### Docker Deployment

1. Build the image:
```bash
docker build -t job-board-api .
```

2. Run the container:
```bash
docker run -p 8000:8000 job-board-api
```

### Production Considerations

- Use PostgreSQL for production database
- Configure proper CORS settings
- Set up email service for notifications
- Implement rate limiting
- Use HTTPS in production
- Configure logging and monitoring
- Set up CI/CD pipeline

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the API documentation at `/docs`

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
  - User management (registration, authentication)
  - Job management (CRUD operations)
  - Application management
  - Role-based access control
  - JWT authentication
  - Comprehensive API documentation 