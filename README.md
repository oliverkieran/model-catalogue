# AI Model Catalogue

A full-stack web application for tracking AI model performance on academic benchmarks and aggregating public opinions from various sources.

## Key Features

- 📊 **Model Catalogue**: Browse and search AI models with their benchmark scores
- 🤖 **LLM-Powered Extraction**: Paste text and automatically extract model information using Claude API
- 📰 **Automated RSS Ingestion**: Daily processing of newsletter feeds (weekdays only)
- 📈 **Benchmark Visualization**: Compare model performance across different benchmarks

## 🛠️ Technology Stack

### Backend

- **Python 3.13+** with **FastAPI** (async web framework)
- **Supabase** (managed PostgreSQL) with **SQLModel** (unified SQLAlchemy + Pydantic)
- **Anthropic Claude API** for LLM-powered data extraction
- **APScheduler** for automated RSS processing
- **pytest** for testing

### Frontend

- **React 18** with **TypeScript**
- **Vite** for build tooling
- **shadcn/ui** component library
- **TanStack Query** for state management

### Deployment

- **Docker Compose** for backend and frontend
- **Supabase Cloud** for managed database
- **VPS** deployment with **nginx** reverse proxy

## 🚀 Getting Started

### Prerequisites

- Python 3.13 or higher
- Node.js 18+ and npm
- Supabase account (free tier available at https://supabase.com)
- Docker and Docker Compose (for containerized setup)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies with uv
uv sync

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# - Create a Supabase project at https://supabase.com
# - Copy the database connection string from Project Settings → Database
# - Add your Anthropic API key
# - Set RSS feed URL

# Run tests to verify setup
uv run pytest

# Start development server
uv run uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

**Interactive API Documentation:**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Available Endpoints:**

- `GET /api/v1/models` - List all models with pagination
- `GET /api/v1/models/{id}` - Get model by ID
- `GET /api/v1/models/search?q=query` - Search models
- `POST /api/v1/models` - Create new model
- `PATCH /api/v1/models/{id}` - Update model
- `DELETE /api/v1/models/{id}` - Delete model
- `GET /api/v1/models/{id}/benchmarks` - Get model's benchmark results
- `GET /api/v1/benchmarks` - List all benchmarks
- `POST /api/v1/benchmarks` - Create benchmark
- `GET /api/v1/benchmark-results` - List benchmark results with filtering
- `POST /api/v1/benchmark-results` - Create benchmark result

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# VITE_API_BASE_URL=http://localhost:8000

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173

**Note:** Make sure the backend server is running on port 8000 for the frontend to fetch data.

## 🧪 Testing

```bash
# Run all tests
cd backend
uv run pytest

# Run with coverage report
uv run pytest --cov=app

# Run only unit tests (fast, mocked)
uv run pytest -m unit

# Run only integration tests (with real database)
uv run pytest -m integration

# Run specific test file
uv run pytest tests/test_repositories.py -v

# Run with verbose output
uv run pytest -v
```

## Git Hooks

This repo ships a [pre-commit](https://pre-commit.com/) configuration that runs Ruff on any staged files inside `backend/`. To enable the hook locally:

```bash
uv tool install pre-commit  # or pip install pre-commit
pre-commit install          # installs the hooks for this repo
```

After installation, `pre-commit` automatically executes the Ruff hook (powered by `ruff-pre-commit`) before each commit, helping block backend lint regressions.
