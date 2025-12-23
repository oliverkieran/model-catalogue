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
- **Module 1.1**: Database Design & Setup (✅ Complete)
- **Module 1.2**: SQLAlchemy Models & Repository Pattern (✅ Complete)
- **Module 2.1**: Pydantic Schemas & API Foundation
- **Module 2.2**: CRUD Endpoints & Error Handling
- **Module 3.1**: LLM Service Layer
- **Module 3.2**: Manual Input Endpoint
- **Module 4.1**: RSS Feed Parser & Scheduler
- **Module 4.2**: Automated Extraction Pipeline
- **Module 5.x**: Frontend Development
- **Module 6.x**: Deployment & Operations

See `modules/` directory for detailed implementation guides.
