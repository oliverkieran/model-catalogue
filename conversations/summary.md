# Project Summary: AI Model Catalogue - Learning Project

## Project Overview

**Goal:** Build a comprehensive AI model catalogue system that tracks model performance on benchmarks and aggregates public opinions from various sources.

**Project Type:** Learning project with tutorial-style implementation to teach software engineering best practices.

**Key Stakeholder:** Oliver - Python developer interested in AI/ML, comfortable with modern tech stacks, wants hands-on learning experience with deployment.

---

## Functional Requirements

### Core Features

1. **Model Catalogue:** Store and display AI models with their benchmark performance scores
2. **Benchmark Tracking:** Academic benchmarks (MMLU, HumanEval, etc.) with scores and sources
3. **Opinion Aggregation:** Track public opinions including:
   - General sentiment
   - Mentioned use cases
   - Community feedback
4. **Automated Data Ingestion:** Daily RSS feed processing (Mon-Fri) from existing newsletter
   - Newsletter is structured with clear bullet points
   - Already exists and summarizes Reddit/Twitter threads
5. **Manual Data Entry:** LLM-powered extraction from pasted text
   - User pastes arbitrary text
   - LLM extracts relevant model/benchmark/opinion information
   - Adds to database

### Scale Expectations

- **Initial:** Few dozen models
- **Growth potential:** Up to 100 models
- **Update frequency:** Daily (weekdays only)

---

## Technical Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (React)                    │
│              shadcn/ui + TanStack Query                  │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   CRUD API   │  │  Manual LLM  │  │ RSS Ingestion│  │
│  │   Endpoints  │  │  Extraction  │  │  + Scheduler │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │ SQLAlchemy
┌────────────────────▼────────────────────────────────────┐
│           Supabase (Managed PostgreSQL)                  │
│  (Relational tables + JSONB for flexible fields)        │
│  + Automatic backups + Database UI                       │
└─────────────────────────────────────────────────────────┘
```

### Data Model (Core Entities)

1. **Models:** id, name, organization, release_date, description, metadata (JSONB)
2. **Benchmarks:** id, name, category, description, url
3. **BenchmarkResults:** id, model_id, benchmark_id, score, date_tested, source
4. **Opinions:** id, model_id, content, sentiment, source, date_published, tags
5. **UseCases:** id, model_id, use_case, description, mentioned_by

---

## Agreed Technology Stack

### Backend

- **Language:** Python 3.13+
- **Framework:** FastAPI (async-capable, auto API docs)
- **Database:** Supabase (managed PostgreSQL) with JSONB for flexible fields
- **ORM:** SQLAlchemy with Alembic migrations
- **Dependency Management:** uv
- **RSS Parsing:** feedparser
- **Scheduling:** APScheduler (for daily newsletter checks)
- **LLM Integration:** Anthropic SDK (Claude API)
- **Validation:** Pydantic
- **Testing:** pytest

### Frontend

- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **UI Components:** shadcn/ui with Tailwind CSS
- **State Management:** TanStack Query (React Query)
- **Routing:** React Router

### Deployment

- **Platform:** VPS with Docker Compose
- **Containers:** Backend (FastAPI), Frontend (nginx), Reverse Proxy (nginx/Caddy)
- **Database:** Supabase Cloud (managed, no container needed)
- **SSL:** Let's Encrypt
- **Why VPS:** Cost-effective, full control, great for learning, production-ready
- **Why Supabase:** Managed database, automatic backups, easier deployment, built-in UI

### Development Tools

- **Containerization:** Docker + Docker Compose
- **Testing:** pytest with fixtures
- **Version Control:** Git with conventional commits

---

## Key Design Decisions

### 1. Separate LLM Extraction Services

- **Manual input:** Dedicated endpoint and service for user-pasted text
- **Newsletter ingestion:** Separate automated pipeline with scheduling
- **Rationale:** Different prompts, processing patterns, and error handling needs

### 2. Supabase (Managed PostgreSQL) Choice

- **Managed Service:** No database DevOps - automatic backups, scaling, monitoring
- **PostgreSQL Foundation:** Same flexibility with ALTER TABLE and Alembic migrations
- **JSONB columns:** For flexible metadata and evolving opinion structures
- **Developer Experience:** Built-in database UI (Supabase Studio) for easy management
- **Cost-Effective:** Free tier suitable for learning projects, easy to self-host PostgreSQL later if needed

### 3. Repository Pattern

- Abstracts database operations from business logic
- Enables easier testing and future database changes
- Follows domain-driven design principles

### 4. Frontend: React + shadcn/ui

- Modern, component-based architecture
- shadcn/ui provides high-quality, customizable components
- TypeScript for type safety (optional but recommended)

### 5. Docker Compose Deployment

- Single VPS hosts backend and frontend containers
- Database hosted on Supabase Cloud (no database container)
- Simplified orchestration and updates
- Full control for learning purposes
- Production-ready with proper configuration
- Easier to manage without database container complexity

---

## Implementation Plan Structure

### Learning Approach

- **Tutorial-style modules:** Step-by-step with explanations
- **Best practices emphasis:** Software engineering principles taught throughout
- **Testing from day one:** Test-driven development mindset
- **Incremental complexity:** Build foundation first, add features progressively

### Module Organization (7 Phases, 16 Modules)

**Phase 0: Project Setup**

- Module 0: Project initialization, structure, git workflow

**Phase 1: Database Layer** (4 hours)

- Module 1.1: Database design, Supabase setup, Alembic
- Module 1.2: SQLAlchemy models, repository pattern

**Phase 2: API Layer** (5 hours)

- Module 2.1: Pydantic schemas, FastAPI foundation
- Module 2.2: CRUD endpoints, error handling

**Phase 3: Manual LLM Input** (4 hours)

- Module 3.1: LLM service layer, prompt engineering
- Module 3.2: Manual input endpoint, processing pipeline

**Phase 4: RSS Newsletter Ingestion** (5 hours)

- Module 4.1: RSS parser, APScheduler setup
- Module 4.2: Automated extraction pipeline

**Phase 5: Frontend** (7 hours)

- Module 5.1: React setup, component architecture
- Module 5.2: Model catalogue UI
- Module 5.3: Manual input interface

**Phase 6: Deployment** (5 hours)

- Module 6.1: Docker configuration (backend + frontend only)
- Module 6.2: Production deployment on VPS with Supabase
- Module 6.3: Maintenance and monitoring

### Estimated Timeline

- **Part-time (5-10 hrs/week):** 5-7 weeks
- **Full-time:** 2 weeks

**Note:** Using Supabase saves ~2-3 hours compared to self-hosted PostgreSQL setup.

---

## Best Practices to Teach Throughout

### Software Engineering

1. **Separation of Concerns:** Models vs Schemas vs Services vs API
2. **Repository Pattern:** Abstract data access layer
3. **Dependency Injection:** FastAPI's DI system
4. **Error Handling:** Proper exceptions and HTTP status codes
5. **API Design:** RESTful conventions, versioning, pagination
6. **Testing Pyramid:** Unit → Integration → E2E

### Development Workflow

1. **Git:** Feature branches, conventional commits
2. **Environment Management:** .env files, configuration classes
3. **Documentation:** Code comments, docstrings, README, API docs
4. **Code Quality:** Type hints, linting, formatting

### Security

1. **Input Validation:** Pydantic schemas
2. **SQL Injection Prevention:** ORM usage, parameterized queries
3. **Secrets Management:** Environment variables, no hardcoded keys
4. **CORS Configuration:** Proper frontend-backend security

### Performance

1. **Database Indexing:** Strategic index placement
2. **Async Operations:** For LLM calls and I/O
3. **Caching:** Development caching for LLM responses
4. **Query Optimization:** Efficient SQLAlchemy queries

### DevOps

1. **Docker Best Practices:** Multi-stage builds, layer caching
2. **Zero-Downtime Deployment:** Rolling updates
3. **Monitoring:** Health checks, logging, error tracking
4. **Backup Strategy:** Supabase automatic backups (built-in)

---

## Next Steps for Curriculum Developer

### Immediate Tasks

1. **Start with Module 0:** Create detailed step-by-step guide for project initialization

   - Directory structure creation
   - uv setup and dependency installation
   - Git repository initialization
   - .gitignore and README templates

2. **Define Learning Objectives:** For each module, clearly state:

   - What the learner will build
   - What concepts they'll learn
   - What skills they'll practice
   - Expected time investment

3. **Create Code Templates:** Provide starter code and completed examples for:
   - Configuration files (pyproject.toml, docker-compose.yml)
   - Base classes (repositories, services)
   - Test fixtures

### Content Development Guidelines

- **Explain the "why":** Don't just show code, explain design decisions
- **Show alternatives:** Mention other approaches and trade-offs
- **Common pitfalls:** Warn about typical mistakes
- **Checkpoints:** Add validation steps ("you should see X")
- **Exercises:** Optional challenges to deepen understanding

### Materials to Prepare

- Code snippets with detailed comments
- Architecture diagrams
- Database schema visualizations
- API endpoint reference
- Testing examples
- Deployment checklists

---

## Open Questions / Future Considerations

1. **Authentication:** Not discussed yet - add later if needed for multi-user scenarios
2. **Frontend deployment:** Static hosting vs same VPS - decided on same VPS with nginx
3. **LLM Provider:** Claude API chosen, but architecture supports swapping providers
4. **Newsletter example:** Will be provided later to inform RSS parsing implementation
5. **Monitoring tools:** Basic logging discussed, could expand to ELK stack or similar
6. **CI/CD:** Not covered in initial plan, could add as optional advanced module

---

## Context Notes

- **Learner background:** Comfortable with Python, strong background in AI/ML, some experience with modern web stacks
- **Learning style preference:** Tutorial-based with hands-on implementation
- **Goal:** Both functional product AND deep understanding of each component
- **Deployment priority:** Real production deployment on VPS, not just local development

This project balances practical application (working catalogue) with educational value (learning full-stack development, deployment, best practices).
