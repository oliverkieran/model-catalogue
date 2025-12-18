# Module 0: Project Setup - Building a Solid Foundation

**Duration:** 30 minutes
**Difficulty:** Beginner
**Prerequisites:** Python 3.13+, Git, basic command line knowledge

---

## Introduction: Why Project Structure Matters

You're about to build a full-stack AI model catalogue—a project that will grow to include a FastAPI backend, React frontend, PostgreSQL database, and LLM integrations. Starting with the right structure isn't just about organization; it's about setting yourself up for success.

A well-structured project makes it easier to:

- **Find things quickly** when you need to fix a bug at 2 AM
- **Onboard collaborators** (or your future self) without confusion
- **Scale gracefully** as features are added
- **Follow best practices** that professional teams use in production

In this module, you'll create the skeleton of your project following Python and TypeScript best practices. Think of it as building the foundation before constructing the house.

---

## What You'll Build

By the end of this module, you'll have:

- ✅ A properly structured project directory with backend and frontend separation
- ✅ Python dependency management configured with `uv`
- ✅ Git repository initialized with proper `.gitignore`
- ✅ Environment configuration setup with `.env` templates
- ✅ Initial documentation (README.md)
- ✅ Testing structure ready to go

---

## Step 1: Create the Root Project Structure

Let's start by creating the top-level directory structure. Open your terminal and run:

```bash
# You should already be in the model-catalogue directory
# Let's verify:
pwd
# Should show: .../model-catalogue

# Create the main directories
mkdir -p backend/{app/{models,schemas,api,services,db},tests,alembic,scripts}
mkdir -p frontend/{src,public}
mkdir -p docker
```

**What just happened?** The `-p` flag creates nested directories in one go. We've created:

- `backend/` - All Python/FastAPI code
- `frontend/` - All React/TypeScript code
- `docker/` - Docker configuration files

Let's verify the structure:

```bash
tree -L 3 -d
```

You should see:

```
.
├── backend
│   ├── alembic
│   ├── app
│   │   ├── api
│   │   ├── db
│   │   ├── models
│   │   ├── schemas
│   │   └── services
│   ├── scripts
│   └── tests
├── conversations
├── docker
├── frontend
│   ├── public
│   └── src
└── modules
```

**🎯 Checkpoint:** You should see the directory tree above. If not, review the `mkdir` command.

---

## Step 2: Initialize Python Project with uv

Modern Python development has evolved. We're using `uv`—a blazingly fast Python package manager that makes dependency management a breeze.

### Install uv (if not already installed)

```bash
# On macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation:
uv --version
```

### Initialize the Python Project

```bash
cd backend

# Initialize a new Python project
uv init --name model-catalogue-api --python 3.13

# This creates pyproject.toml - the modern Python project configuration file
```

Now let's add our initial dependencies:

```bash
# Core dependencies
uv add fastapi uvicorn[standard] sqlalchemy alembic psycopg2-binary pydantic-settings python-dotenv

# LLM and data processing
uv add anthropic feedparser apscheduler

# Development dependencies
uv add --dev pytest pytest-asyncio pytest-cov httpx ruff

# Go back to root
cd ..
```

**Why these dependencies?**

- **fastapi + uvicorn**: Web framework and ASGI server
- **sqlalchemy + alembic**: Database ORM and migrations
- **psycopg2-binary**: PostgreSQL adapter
- **pydantic-settings**: Environment configuration management
- **anthropic**: Claude API client
- **feedparser**: RSS parsing
- **apscheduler**: Task scheduling
- **pytest ecosystem**: Testing framework with async support and coverage
- **httpx**: HTTP client for testing FastAPI
- **ruff**: Fast Python linter and formatter

**🎯 Checkpoint:** Check that `backend/pyproject.toml` exists and contains your dependencies.

### Activate the Virtual Environment

Before creating Python files, let's activate the virtual environment so your IDE can recognize the imports.

`uv` automatically creates a virtual environment at `.venv` next to the `pyproject.toml`. Activate it:

```bash
# Activate the virtual environment
source .venv/bin/activate
```

You should see `(.venv)` appear in your terminal prompt.

**Configure VSCode Python Interpreter:**

If you're using VSCode, set it to use the virtual environment:

1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type "Python: Select Interpreter"
3. Choose the interpreter at `./.venv/bin/python`

Now VSCode will recognize all your installed packages!

**🎯 Checkpoint:** Run `which python` (Mac/Linux) or `where python` (Windows) - it should show the path to `.venv/bin/python`

---

## Step 3: Create Python Package Structure

Python needs `__init__.py` files to recognize directories as packages. Let's create them:

```bash
# Create __init__.py files
touch backend/app/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/api/__init__.py
touch backend/app/services/__init__.py
touch backend/app/db/__init__.py
touch backend/tests/__init__.py
```

Now create the main application entry point by creating a file `backend/app/main.py`

```python
"""
Model Catalogue API - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI application instance
app = FastAPI(
    title="Model Catalogue API",
    description="API for tracking AI model benchmarks and public opinions",
    version="0.1.0",
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Model Catalogue API",
        "status": "operational",
        "version": "0.1.0"
    }


@app.get("/api/v1/health")
async def health_check():
    """Detailed health check for monitoring"""
    return {
        "status": "healthy",
        "database": "not configured yet",
        "llm_service": "not configured yet"
    }
```

Create the configuration module `backend/app/config.py` for managing environment variables using Pydantic Settings:

```python
"""
Application Configuration
Manages environment variables and settings using Pydantic
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Application
    app_name: str = "Model Catalogue API"
    debug: bool = False

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/model_catalogue"

    # LLM Service
    anthropic_api_key: str = ""

    # RSS Feed
    rss_feed_url: str = ""

    # Scheduler
    enable_scheduler: bool = True
    schedule_cron: str = "0 9 * * 1-5"  # 9 AM, Monday-Friday

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
```

**Why Pydantic Settings?** It provides:

- Type validation for environment variables
- Automatic `.env` file loading
- Default values with type hints
- Easy to test (just pass different values)

**🎯 Checkpoint:** Verify you can import the config:

```bash
cd backend
uv run python -c "from app.config import settings; print(settings.app_name)"
cd ..
```

You should see: `Model Catalogue API`

---

## Step 4: Initialize Git Repository

Version control is essential. Let's set up Git properly from the start.

If you haven't already initialized a Git repository, do so now: `git init`

Next, create a `.gitignore` file at the root of your project:

```bash
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Environment variables
.env
.env.local
.env.*.local

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Database
*.db
*.sqlite3

# Logs
*.log
logs/

# Frontend
node_modules/
frontend/dist/
frontend/build/
frontend/.vite/

# Docker
docker-compose.override.yml

# OS
.DS_Store
Thumbs.db
```

**Why this .gitignore?** It prevents committing:

- Virtual environments and dependencies (should be recreated)
- Environment variables (contain secrets!)
- IDE-specific files (personal preference)
- Build artifacts (generated, not source)
- Logs and databases (too large, not code)

Now create the initial commit:

```bash
git add .
git commit -m "chore: initial project structure setup

- Created backend and frontend directory structure
- Configured Python dependencies with uv
- Added FastAPI application skeleton
- Configured Pydantic settings management
- Added comprehensive .gitignore"
```

**Note the commit message format:** We're using [Conventional Commits](https://www.conventionalcommits.org/):

- `chore:` for maintenance tasks
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation

**🎯 Checkpoint:** Verify your commit:

```bash
git log --oneline
```

---

## Step 5: Environment Configuration

Never hardcode secrets! Let's create environment templates.

Create a `.env.example` file at the root of your project:

```bash
# Application Settings
APP_NAME="Model Catalogue API"
DEBUG=False

# Database Configuration
# Format: postgresql://user:password@host:port/database
DATABASE_URL=postgresql://catalogue_user:your_secure_password@localhost:5432/model_catalogue

# Anthropic API (Claude)
# Get your API key from: https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# RSS Feed URL
RSS_FEED_URL=https://your-newsletter-feed-url.com/rss

# Scheduler Configuration
ENABLE_SCHEDULER=True
SCHEDULE_CRON="0 9 * * 1-5"
```

and copy it to create your actual `.env` file:

`cp .env.example .env`

**Security Note:** The `.env` file is in `.gitignore` and will never be committed. The `.env.example` shows the structure without exposing secrets.

**🎯 Checkpoint:** Verify environment loading works:

```bash
cd backend
echo 'APP_NAME="My Test App"' > ../.env
uv run python -c "from app.config import settings; print(settings.app_name)"
cd ..
```

---

## Step 6: Create Initial Tests Structure

Testing from day one! Let's set up the testing infrastructure.

First, create a `pytest.ini` file in the `backend/` directory:

`touch backend/pytest.ini`

```bash
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

Then create a `conftest.py` file in `backend/tests/` for shared fixtures:

```python
"""
Pytest configuration and shared fixtures
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application
    """
    return TestClient(app)

@pytest.fixture
def sample_model_data():
    """
    Sample model data for testing
    """
    return {
        "name": "GPT-4",
        "organization": "OpenAI",
        "release_date": "2023-03-14",
        "description": "Large multimodal model"
    }
```

Now create a sample test file `backend/tests/test_main.py` to test the main application endpoints:

```python
"""
Tests for main application endpoints
"""
import pytest

def test_root_endpoint(client):
    """Test the root endpoint returns expected response"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"

@pytest.mark.slow
def test_placeholder_slow():
    """Example of a slow test (like LLM API calls)"""
    pass

```

Run the tests to verify everything works:

```bash
cd backend
uv run pytest
cd ..
```

You should see:

```
collected 3 items

tests/test_main.py::test_root_endpoint PASSED
tests/test_main.py::test_health_check PASSED
tests/test_main.py::test_placeholder_slow PASSED

====== 3 passed in 0.XX s ======
```

**Why test fixtures?** The `@pytest.fixture` decorator creates reusable test components. The `client` fixture gives you a test client for making requests without starting a server.

**🎯 Checkpoint:** All tests should pass. If not, check that your `main.py` is correct.

---

## Step 7: Create Project Documentation

Every project needs a README. Let's create one:

````bash
# AI Model Catalogue

A full-stack web application for tracking AI model performance on academic benchmarks and aggregating public opinions from various sources.

## 🎯 Project Overview

This is a learning project designed to teach full-stack software engineering best practices through hands-on implementation. The application tracks:

- **AI Models**: Names, organizations, release dates, and metadata
- **Benchmark Results**: Performance scores on academic benchmarks (MMLU, HumanEval, etc.)
- **Public Opinions**: Sentiment, use cases, and community feedback from various sources

### Key Features

- 📊 **Model Catalogue**: Browse and search AI models with their benchmark scores
- 🤖 **LLM-Powered Extraction**: Paste text and automatically extract model information using Claude API
- 📰 **Automated RSS Ingestion**: Daily processing of newsletter feeds (weekdays only)
- 📈 **Benchmark Visualization**: Compare model performance across different benchmarks

## 🛠️ Technology Stack

### Backend
- **Python 3.13+** with **FastAPI** (async web framework)
- **PostgreSQL** with SQLAlchemy ORM
- **Anthropic Claude API** for LLM-powered data extraction
- **APScheduler** for automated RSS processing
- **pytest** for testing

### Frontend
- **React 18** with **TypeScript**
- **Vite** for build tooling
- **shadcn/ui** component library
- **TanStack Query** for state management

### Deployment
- **Docker Compose** for local development and production
- **VPS** deployment with **nginx** reverse proxy

## 🚀 Getting Started

### Prerequisites

- Python 3.13 or higher
- Node.js 18+ and npm
- PostgreSQL 15+
- Docker and Docker Compose (for containerized setup)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies with uv
uv sync

# Copy environment template
cp ../.env.example ../.env

# Edit .env with your configuration
# - Add your Anthropic API key
# - Configure database URL
# - Set RSS feed URL

# Run tests to verify setup
uv run pytest

# Start development server
uv run uvicorn app.main:app --reload
````

The API will be available at http://localhost:8000

API documentation (auto-generated): http://localhost:8000/docs

### Frontend Setup (Coming in Phase 5)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173

## 📁 Project Structure

```
model-catalogue/
├── backend/                  # Python FastAPI backend
│   ├── app/
│   │   ├── main.py          # Application entry point
│   │   ├── config.py        # Settings management
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── api/             # API route handlers
│   │   ├── services/        # Business logic layer
│   │   └── db/              # Database utilities
│   ├── tests/               # Test suite
│   ├── alembic/             # Database migrations
│   └── pyproject.toml       # Python dependencies
├── frontend/                 # React frontend (Phase 5)
│   └── src/
├── docker/                   # Docker configuration
├── modules/                  # Learning modules documentation
└── README.md
```

## 🧪 Testing

```bash
# Run all tests
cd backend
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run only fast tests (exclude slow LLM tests)
uv run pytest -m "not slow"
```

## 📚 Learning Modules

This project is built following a structured learning path:

- **Module 0**: Project Setup (✅ Complete)
- **Module 1.1**: Database Design & Setup
- **Module 1.2**: SQLAlchemy Models & Repository Pattern
- **Module 2.1**: Pydantic Schemas & API Foundation
- **Module 2.2**: CRUD Endpoints & Error Handling
- **Module 3.1**: LLM Service Layer
- **Module 3.2**: Manual Input Endpoint
- **Module 4.1**: RSS Feed Parser & Scheduler
- **Module 4.2**: Automated Extraction Pipeline
- **Module 5.x**: Frontend Development
- **Module 6.x**: Deployment & Operations

See `modules/` directory for detailed implementation guides.

## 🔒 Security Notes

- Never commit `.env` files (they contain secrets!)
- Use environment variables for all sensitive configuration
- The `.env.example` template shows required variables without exposing secrets

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Project Planning Documents](./conversations/)

**Status**: 🚧 Module 0 Complete - Database layer coming next!

````

**🎯 Checkpoint:** View your README:

```bash
cat README.md
````

---

## Step 8: Verify Everything Works

Let's do a final verification that everything is set up correctly:

```bash
# 1. Check directory structure
echo "=== Directory Structure ==="
tree -L 3 -I '__pycache__|*.pyc|.pytest_cache' backend

# 2. Verify Python dependencies
echo -e "\n=== Python Dependencies ==="
cd backend && uv tree | head -20 && cd ..

# 3. Run tests
echo -e "\n=== Running Tests ==="
cd backend && uv run pytest -v && cd ..

# 4. Start the development server (Ctrl+C to stop)
echo -e "\n=== Starting Development Server ==="
cd backend && uv run uvicorn app.main:app --reload
```

Visit http://localhost:8000 in your browser. You should see:

```json
{
  "message": "Model Catalogue API",
  "status": "operational",
  "version": "0.1.0"
}
```

Visit http://localhost:8000/docs to see the auto-generated API documentation.

**🎯 Final Checkpoint:**

- ✅ Directory structure matches the plan
- ✅ All Python dependencies installed
- ✅ Tests pass successfully
- ✅ Development server runs without errors
- ✅ API documentation loads at /docs

---

## What You've Accomplished

Congratulations! 🎉 You've built a solid foundation for your full-stack application. Here's what you now have:

1. **Organized Project Structure**: Backend and frontend separated cleanly
2. **Modern Python Setup**: Using `uv` for fast dependency management
3. **Configuration Management**: Pydantic settings with environment variables
4. **Working API**: Basic FastAPI application with health checks
5. **Testing Infrastructure**: pytest configured with fixtures
6. **Version Control**: Git repository with proper .gitignore
7. **Documentation**: Comprehensive README

### Key Takeaways

- **Structure matters**: A well-organized project scales better and is easier to navigate
- **Test early**: Having tests from day one prevents regression bugs
- **Security first**: Environment variables keep secrets out of version control
- **Convention over configuration**: Following established patterns (like Conventional Commits) makes collaboration easier

---

## What's Next?

In **Module 1.1**, you'll:

- Design the database schema for models, benchmarks, and opinions
- Set up PostgreSQL with Docker Compose
- Initialize Alembic for database migrations
- Create your first migration

The foundation is laid. Now it's time to build the data layer!

---

## Troubleshooting

### `uv: command not found`

Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Tests fail with import errors

Make sure you're in the `backend/` directory and running: `uv run pytest`

### Port 8000 already in use

Kill the existing process: `lsof -ti:8000 | xargs kill -9`

Or use a different port: `uvicorn app.main:app --reload --port 8001`

### Dependencies not found

Sync dependencies: `cd backend && uv sync`

---

## Additional Resources

- [uv documentation](https://github.com/astral-sh/uv)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Python Project Structure Guide](https://docs.python-guide.org/writing/structure/)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)

---

**Next Module**: [Module 1.1 - Database Design & Setup](./module-1.1-database-design.md)
