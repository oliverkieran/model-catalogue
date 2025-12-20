# CLAUDE.md

## Project Overview

**AI Model Catalogue** - A full-stack web application for tracking AI model performance on benchmarks and aggregating public opinions from various sources. This is a learning project designed to teach software engineering best practices through hands-on implementation.

**Current Status:** Planning phase - implementation not yet started. The project structure and technical architecture are defined in `/conversations/`.

## Technology Stack

### Backend

- **Python 3.13+** with **FastAPI** (async web framework)
- **Supabase** (managed PostgreSQL) with JSONB for flexible metadata storage
- **SQLModel** (combines SQLAlchemy and Pydantic) with **Alembic** migrations
- **uv** for dependency management
- **pytest** for testing
- **Anthropic SDK** (Claude API) for LLM-powered data extraction
- **feedparser** for RSS parsing
- **APScheduler** for scheduled tasks (weekday newsletter ingestion)

### Frontend

- **React 18** with **TypeScript**
- **Vite** for build tooling
- **shadcn/ui** component library with **Tailwind CSS**
- **TanStack Query** (React Query) for state management
- **React Router** for routing

### Deployment

- **Docker Compose** for backend/frontend orchestration
- **Supabase Cloud** for managed database (no database container needed)
- **VPS** deployment target
- **nginx/Caddy** for reverse proxy
- **Let's Encrypt** for SSL

## Architecture Pattern

### Directory Structure (Planned)

```
model-catalogue/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry
│   │   ├── config.py               # Settings management
│   │   ├── models/                 # SQLModel models (table & schema)
│   │   ├── schemas/                # Additional Pydantic schemas if needed
│   │   ├── api/                    # API route handlers
│   │   ├── services/               # Business logic layer
│   │   └── db/                     # Database utilities & repositories
│   ├── tests/
│   │   ├── conftest.py             # pytest fixtures
│   │   └── test_*.py
│   ├── alembic/                    # Database migrations
│   └── scripts/                    # Utility scripts
├── frontend/
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── pages/                  # Route pages
│   │   ├── lib/                    # Utilities
│   │   ├── hooks/                  # Custom hooks
│   │   └── api/                    # API client
│   └── package.json
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
└── docker-compose.yml
```

### Core Design Patterns

**Repository Pattern:** All database operations are abstracted through repository classes (e.g., `ModelRepository`, `BenchmarkRepository`) that inherit from `BaseRepository`. This separates data access from business logic.

**Service Layer:** Business logic lives in service classes (e.g., `LLMService`, `ExtractionService`) that orchestrate repositories and external APIs. Services are injected into API endpoints via FastAPI's dependency injection.

**Unified Models with SQLModel:** SQLModel combines database models and Pydantic schemas into a single source of truth, reducing duplication:

- Base `SQLModel` class defines shared fields
- Table models (with `table=True`) represent database tables
- Schema models inherit from base for API requests/responses (`*Create`, `*Update`, `*Response`)
- Eliminates the need for separate ORM and Pydantic model definitions

**Async-First:** Use async/await throughout for I/O operations (database queries, LLM API calls, RSS fetching). SQLModel uses SQLAlchemy's `AsyncSession` for async database operations.

## Data Model

### Core Entities

1. **Models** - AI models (id, name, organization, release_date, description, metadata JSONB)
2. **Benchmarks** - Academic benchmarks (id, name, category, description, url)
3. **BenchmarkResults** - Model performance scores (id, model_id, benchmark_id, score, date_tested, source)
4. **Opinions** - Public opinions (id, model_id, content, sentiment, source, date_published, tags[])
5. **UseCases** - Mentioned use cases (id, model_id, use_case, description, mentioned_by)

Use JSONB columns for flexible metadata that may evolve over time.

## Key Features

### 1. Manual LLM-Powered Data Entry

- User pastes arbitrary text
- Claude API extracts structured data (models, benchmarks, opinions)
- Validation before database insertion
- Endpoint: `POST /api/v1/extract`

### 2. Automated RSS Newsletter Ingestion

- Scheduled job runs Monday-Friday
- APScheduler fetches RSS feed from existing newsletter
- Claude API processes structured newsletter content
- Automatic database updates with deduplication

### 3. Model Catalogue UI

- Browse/search AI models
- View benchmark results with visualizations
- Filter and sort functionality
- Responsive design with shadcn/ui components

## Development Commands

### Backend (when implemented)

```bash
# Install dependencies
uv pip install

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Create database migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Run linter/formatter
ruff check .
ruff format .
```

### Supabase (Local Development - Optional)

```bash
# Start local Supabase stack (PostgreSQL + Studio UI)
supabase start

# Stop local Supabase
supabase stop

# Reset local database
supabase db reset

# Push migrations to Supabase (alternative to alembic)
supabase db push
```

**Note:** You can develop using either:

- **Option A:** Supabase Cloud dev project (simpler, no local database)
- **Option B:** Local Supabase CLI (recommended, works offline)

### Frontend (when implemented)

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Type checking
npm run type-check
```

### Docker

```bash
# Start all services (backend + frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild after changes
docker-compose up -d --build

# Stop services
docker-compose down
```

**Note:** The PostgreSQL database is hosted on Supabase, so there's no database container in docker-compose.yml.

## Testing Strategy

Follow the testing pyramid:

1. **Unit tests** - Repository methods, service logic, schema validation
2. **Integration tests** - API endpoints with test database, LLM service with mocked responses
3. **E2E tests** - Full extraction pipeline, RSS ingestion workflow

Use pytest fixtures for:

- Test database sessions
- Sample data (models, benchmarks)
- Mocked LLM responses (to avoid API costs)

Mark slow tests (real LLM API calls) with `@pytest.mark.slow` and exclude from default test runs.

## API Design Conventions

- Base path: `/api/v1/`
- RESTful resource naming (plural nouns)
- Pagination on list endpoints: `?skip=0&limit=20`
- Search via query param: `?q=search_term`
- Related resources: `/api/v1/models/{id}/benchmarks`
- Consistent error responses with detail messages
- Proper HTTP status codes (200, 201, 400, 404, 500)

## LLM Integration Guidelines

**Prompt Engineering:**

- Store prompt templates in configuration (not hardcoded in services)
- Use Claude's structured output features (JSON mode)
- Include examples in prompts for better extraction accuracy

**Cost Management:**

- Cache LLM responses during development
- Log token usage for monitoring
- Use appropriate model tiers (Haiku for simple tasks, Sonnet for complex extraction)

**Error Handling:**

- Retry logic with exponential backoff
- Graceful degradation on API failures
- Validate LLM outputs against schemas

## Environment Configuration

Use `.env` files for local development. Required variables:

```bash
# Supabase Database Connection
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# Supabase URLs (Optional - only if using Supabase client directly)
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...

# LLM Integration
ANTHROPIC_API_KEY=sk-ant-...

# RSS Feed
RSS_FEED_URL=https://...

# API Configuration
CORS_ORIGINS=http://localhost:5173
LOG_LEVEL=INFO
```

Never commit secrets. Use `.env.example` for templates.

**Getting Supabase Credentials:**

1. Create a project at https://supabase.com
2. Go to Project Settings → Database
3. Copy the connection string (set mode to "Session")
4. Find API keys in Project Settings → API

## Git Workflow

Use conventional commits format:

- `feat:` new features
- `fix:` bug fixes
- `refactor:` code refactoring
- `test:` test additions/changes
- `docs:` documentation updates
- `chore:` maintenance tasks

Feature branch workflow recommended:

```bash
git checkout -b feat/model-repository
# make changes
git commit -m "feat: implement model repository with CRUD operations"
git push origin feat/model-repository
# create PR
```

## Security Considerations

- **Input Validation:** All user input validated via SQLModel/Pydantic schemas
- **SQL Injection Prevention:** Use SQLModel ORM (built on SQLAlchemy), never raw SQL with user input
- **Secrets Management:** Environment variables only, never hardcoded
- **CORS:** Configure allowed origins explicitly
- **Rate Limiting:** Consider for public API endpoints (future enhancement)

## Performance Optimization

- **Database Indexing:** Add indexes on frequently queried fields (model.name, benchmark_results.model_id, opinions.model_id)
- **Query Optimization:** Use SQLAlchemy's eager loading (`joinedload`, `selectinload`) to avoid N+1 queries (SQLModel uses SQLAlchemy underneath)
- **Async Operations:** All I/O operations should be async (database with `AsyncSession`, LLM API, RSS fetching)
- **Response Caching:** Consider caching for read-heavy endpoints (future enhancement)

## Implementation Phases

The project follows a 6-phase implementation plan (see `/conversations/initial-plan.md`):

1. **Phase 0:** Project setup and structure
2. **Phase 1:** Database layer with SQLModel models and repositories (using Supabase)
3. **Phase 2:** FastAPI endpoints with SQLModel schemas
4. **Phase 3:** Manual LLM input processing
5. **Phase 4:** Automated RSS newsletter ingestion
6. **Phase 5:** React frontend
7. **Phase 6:** Docker deployment (simplified - no database container)

When implementing, follow the modular approach: complete one phase before moving to the next, with tests at each stage.

**Note on Phase 1:** Instead of setting up a local PostgreSQL container, you'll create a Supabase project and connect to it. SQLModel combines database models and Pydantic schemas into unified definitions, reducing code duplication while teaching the same ORM patterns (it's built on SQLAlchemy).

## References

- Project planning: `/conversations/summary.md`
- Detailed implementation plan: `/conversations/initial-plan.md`
- FastAPI docs: https://fastapi.tiangolo.com/
- SQLModel docs: https://sqlmodel.tiangolo.com/
- SQLAlchemy 2.0 docs: https://docs.sqlalchemy.org/ (SQLModel is built on this)
- shadcn/ui: https://ui.shadcn.com/
- Anthropic API docs: https://docs.anthropic.com/
