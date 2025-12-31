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

## 📚 Learning Modules

This project is built following a structured learning path:

### Completed Modules ✅

- **Module 0**: Project Setup
- **Module 1.1**: Database Design & Setup
- **Module 1.2**: Repository Pattern
- **Module 2.1**: SQLModel Schemas & API Foundation
- **Module 2.2**: CRUD Operations & Error Handling
- **Module 3.1**: LLM Integration Basics
- **Module 4.1**: Frontend Development

### Next Modules (Planned)

- **Module 3.2**: Manual Input Endpoint
- **Module 4.2**: CRUD UI & Form Handling
- **Module 5**: RSS Feed Parser & Scheduler
- **Module 6**: Deployment & Operations

See `modules/` directory for detailed implementation guides.

## 📊 Current Implementation Status

**Backend (85% complete):**
- ✅ Database layer with SQLModel models and repositories
- ✅ Core CRUD API endpoints (Models, Benchmarks, BenchmarkResults)
- ✅ Request/response validation with Pydantic schemas
- ✅ Error handling with proper HTTP status codes
- ✅ CORS configuration for frontend integration
- ✅ Unit and integration tests
- ✅ LLM integration
- ⏳ RSS feed processing (Module 5 - planned)

**Frontend (60% complete):**
- ✅ React 18 + TypeScript setup with Vite
- ✅ shadcn/ui component library integrated
- ✅ API client with Axios and error handling
- ✅ TanStack Query for data fetching and caching
- ✅ TypeScript types matching backend schemas
- ✅ Model browsing with search and filtering
- ✅ Responsive UI with loading/error states
- ✅ Model comparison feature
- ⏳ CRUD forms for creating/editing (Module 4.2 - planned)
- ⏳ Admin panel (Module 4.2 - planned)

**Deployment:** Not yet started (Module 6 - planned)
