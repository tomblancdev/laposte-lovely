# Django Overtuned

A modern, full-stack web application template that combines Django's robust backend capabilities with Next.js frontend, providing a comprehensive foundation for building scalable web applications.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-5.2.7-green.svg)](https://docs.djangoproject.com/)
[![Next.js](https://img.shields.io/badge/next.js-16.0.1-black.svg)](https://nextjs.org/)

License: MIT

## 🚀 Features

### Backend (Django)

- **Django 5.2.7** with modern Python 3.12+ support
- **Django REST Framework** for API development
- **Django Allauth** with MFA support for authentication
- **Celery** for background task processing with Redis
- **PostgreSQL** database with optimized configuration
- **Automatic API documentation** with drf-spectacular
- **Comprehensive test suite** with pytest and coverage
- **Code quality tools**: Ruff, mypy, djLint

### Frontend (Next.js)

- **Next.js 16** with React 19 and TypeScript
- **Tailwind CSS 4** for modern styling
- **OpenAPI integration** with automatic type generation
- **Authentication flows** integrated with Django backend
- **Modern build tools**: Turbopack, Biome

### DevOps & Infrastructure

- **Docker Compose** setup for local development and production
- **Multi-environment configuration** (local, production, test)
- **Automated schema generation** between backend and frontend
- **Email testing** with Mailpit
- **Task automation** with Just
- **Internationalization** support (English, French, Portuguese)

## 🏗️ Architecture

```text
django-overtuned/
├── backend/          # Django application
│   ├── config/       # Django settings and configuration
│   ├── django_overtuned/  # Main Django app
│   └── requirements/ # Python dependencies
├── frontend/         # Next.js application
│   ├── app/         # Next.js app directory
│   ├── components/  # Reusable React components
│   └── types/       # TypeScript type definitions
├── compose/         # Docker configuration
├── scripts/         # Utility scripts
└── docs/           # Documentation
```

## 🚀 Quick Start

### Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose
- [Just](https://github.com/casey/just) (optional, for task automation)

### Local Development Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd django-overtuned
   ```

2. **Start the development environment**

   ```bash
   # Using Just (recommended)
   just up

   # Or using Docker Compose directly
   docker compose -f docker-compose.local.yml up -d
   ```

3. **Access the applications**

   - **Frontend (Next.js)**: <http://localhost:3000>
   - **Backend API**: <http://localhost:8000>
   - **Admin Panel**: <http://localhost:8000/admin>
   - **API Documentation**: <http://localhost:8000/api/schema/swagger-ui/>
   - **Email Testing (Mailpit)**: <http://localhost:8025>
   - **Flower (Celery monitoring)**: <http://localhost:5555>

4. **Create a superuser account**

   ```bash
   just manage createsuperuser
   ```

### Available Commands

Using Just (task runner):

```bash
just                    # List all available commands
just build             # Build Docker images
just up                # Start all services
just down              # Stop all services
just logs              # View container logs
just manage <command>  # Run Django management commands
```

### Project Renaming

The project includes cross-platform scripts to rename all project components (Docker images, containers, configurations) to your preferred name:

**Linux/macOS (Bash):**

```bash
bash scripts/rename-project.sh [new-project-name]
```

**Windows (PowerShell):**

```powershell
.\scripts\rename-project.ps1 [new-project-name]
```

**Windows (Command Prompt):**

```cmd
scripts\rename-project.cmd [new-project-name]
```

These scripts will:

- Prompt for a new project name if not provided
- Automatically slugify the name (lowercase, alphanumeric, `_`, `-`)
- Update all Docker Compose files and dev container configuration
- Confirm changes before applying them

**Example:**

```bash
bash scripts/rename-project.sh "my-awesome-app"
# Updates docker-compose.*.yml and .devcontainer/devcontainer.json
# Renames images from django-overtuned_* to my-awesome-app_*
```

## 📋 Development Workflow

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

  ```bash
  just manage createsuperuser
  # Or directly with Docker Compose
  docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser
  ```

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Code Quality and Testing

#### Type Checking

Running type checks with mypy:

```bash
# Inside the Django container
docker compose -f docker-compose.local.yml run --rm django mypy django_overtuned
```

#### Test Coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

```bash
# Run tests with coverage
docker compose -f docker-compose.local.yml run --rm django coverage run -m pytest
docker compose -f docker-compose.local.yml run --rm django coverage html
```

#### Running Tests

```bash
# Run all tests
docker compose -f docker-compose.local.yml run --rm django pytest

# Run specific test file
docker compose -f docker-compose.local.yml run --rm django pytest path/to/test_file.py
```

### API Schema Generation

Generate TypeScript types from Django API schemas:

```bash
just manage shell -c "from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'spectacular', '--color', '--file', '/tmp/schema.yml'])"
bash scripts/generate-schemas.sh
```

Or use the available task:

```bash
# This will generate TypeScript types for the frontend
bash /app/scripts/generate-schemas.sh
```

### Background Tasks with Celery

This application includes Celery for handling background tasks. The Docker setup automatically starts:

- **Celery Worker**: Processes background tasks
- **Celery Beat**: Handles periodic/scheduled tasks
- **Flower**: Web-based monitoring tool at <http://localhost:5555>

To manually run Celery commands:

```bash
# Run a Celery worker
docker compose -f docker-compose.local.yml run --rm django celery -A config.celery_app worker -l info

# Run Celery beat scheduler
docker compose -f docker-compose.local.yml run --rm django celery -A config.celery_app beat

# Monitor tasks with Flower (already running in Docker setup)
# Access at http://localhost:5555
```

### Email Testing

The development environment includes [Mailpit](https://github.com/axllent/mailpit) for email testing:

- **Email interface**: <http://localhost:8025>
- All emails sent by the application are captured and displayed
- No actual emails are sent in development
- Container starts automatically with `just up`

### Frontend Development

The Next.js frontend supports:

- **Hot reloading**: Changes are reflected immediately
- **TypeScript**: Full type safety with auto-generated API types
- **Tailwind CSS**: Utility-first styling with Tailwind 4
- **Modern tooling**: Turbopack for fast builds, Biome for linting

Frontend development commands:

```bash
# Start development server (already running in Docker)
cd frontend && npm run dev

# Build for production
cd frontend && npm run build

# Run linting
cd frontend && npx biome check .
```

### Monitoring and Observability

#### Sentry Integration

Sentry is configured for error logging and performance monitoring:

- Sign up at <https://sentry.io/signup/?code=cookiecutter>
- Set the `SENTRY_DSN` environment variable in production
- Automatic error capturing with 404 logging
- WSGI application integration included

## 🚢 Deployment

### Production Deployment

The project includes production-ready Docker configurations:

```bash
# Build and start production services
docker compose -f docker-compose.production.yml up -d --build

# Scale services as needed
docker compose -f docker-compose.production.yml up -d --scale django=3
```

#### Production Services

- **Django**: ASGI application with Uvicorn
- **Next.js**: Static export or SSR configuration
- **PostgreSQL**: Production database with backup utilities
- **Redis**: Session storage and Celery broker
- **Nginx**: Reverse proxy and static file serving
- **Traefik**: Load balancing and SSL termination

#### Environment Configuration

Create production environment files:

```bash
# Required environment files for production
.envs/.production/.django
.envs/.production/.postgres
.envs/.production/.nextjs
```

Key production settings:

- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS`
- Set secure `SECRET_KEY`
- Configure database credentials
- Set up Sentry DSN
- Configure email backend (SMTP)

### CI/CD Pipeline

The project structure supports modern CI/CD workflows:

- **Testing**: Automated test runs with pytest
- **Code Quality**: Ruff, mypy, and Biome checks
- **Type Safety**: Automatic API schema generation
- **Container Builds**: Multi-stage Docker builds
- **Security Scanning**: Dependency vulnerability checks

## 🛠️ Development Tools

### Code Quality

- **Ruff**: Fast Python linter and formatter
- **mypy**: Static type checking for Python
- **djLint**: Django template linting
- **Biome**: Fast formatter/linter for TypeScript/JavaScript
- **Pre-commit hooks**: Automated code quality checks

### Testing

- **pytest**: Python testing framework
- **Coverage.py**: Code coverage reporting
- **Factory Boy**: Test data generation
- **Django Test Client**: API endpoint testing

### Development Utilities

- **Just**: Task runner with predefined commands
- **Docker Compose**: Consistent development environment
- **Hot reload**: Both Django and Next.js support live reloading
- **Debug toolbar**: Django debug toolbar in development
- **Project renaming scripts**: Cross-platform scripts to rename the entire project

## 📚 Documentation

### API Documentation

- **Swagger UI**: Interactive API documentation at `/api/schema/swagger-ui/`
- **ReDoc**: Alternative API docs at `/api/schema/redoc/`
- **OpenAPI Schema**: Machine-readable schema at `/api/schema/`

### Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `just manage test`
5. Submit a pull request

### Development Setup for Contributors

```bash
# Clone your fork
git clone https://github.com/your-username/django-overtuned.git
cd django-overtuned

# Start development environment
just up

# Run tests
just manage test

# Check code quality
docker compose -f docker-compose.local.yml run --rm django ruff check .
docker compose -f docker-compose.local.yml run --rm django mypy django_overtuned
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

Tom Blanc

---

Built with ❤️ using Django, Next.js, and modern development practices.
