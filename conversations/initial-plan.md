# **Model Catalogue - Implementation Plan**

## **Project Setup & Best Practices Foundation**

### **Module 0: Project Initialization**

**Duration:** 30 minutes  
**Learning Goals:** Project structure, dependency management, git workflow

**What you'll build:**

- Repository structure following Python best practices
- Development environment setup
- Git workflow with conventional commits

**Deliverables:**

```
model-catalogue/
├── .gitignore
├── README.md
├── pyproject.toml              # uv configuration
├── .env.example                # Environment template
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py           # Settings management
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── api/                # API routes
│   │   ├── services/           # Business logic
│   │   └── db/                 # Database utilities
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py         # pytest fixtures
│   │   └── test_*.py
│   ├── alembic/                # Database migrations
│   └── scripts/                # Utility scripts
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
└── docker-compose.yml
```

**Best Practices Introduced:**

- Separation of concerns (models vs schemas vs services)
- Environment-based configuration
- Testing structure from day one
- Clear documentation with README

---

## **Phase 1: Database Layer & Core Domain Models**

### **Module 1.1: Database Design & Setup**

**Duration:** 2 hours  
**Learning Goals:** Relational database design, PostgreSQL, Docker basics

**What you'll build:**

- Docker Compose setup for local PostgreSQL
- Database schema design with proper normalization
- Initial migration with Alembic

**Schema Design:**

```python
# Core entities:
- Models (id, name, organization, release_date, description, metadata JSONB)
- Benchmarks (id, name, category, description, url)
- BenchmarkResults (id, model_id, benchmark_id, score, date_tested, source)
- Opinions (id, model_id, content, sentiment, source, date_published, tags[])
- UseCases (id, model_id, use_case, description, mentioned_by)
```

**Best Practices:**

- Database normalization (avoiding redundancy)
- Proper indexing strategy
- JSONB for flexible metadata
- Timestamps and soft deletes
- Foreign key constraints

**Testing:**

- Database connection tests
- Schema validation tests

---

### **Module 1.2: SQLAlchemy Models & Repository Pattern**

**Duration:** 2 hours  
**Learning Goals:** ORM patterns, repository pattern, database sessions

**What you'll build:**

- SQLAlchemy models matching your schema
- Base repository class with CRUD operations
- Specific repositories for each entity
- Database session management

**Example Pattern:**

```python
# Repository pattern - abstracts database operations
class BaseRepository:
    def get_by_id(self, id: int)
    def get_all(self, skip: int, limit: int)
    def create(self, obj)
    def update(self, id: int, obj)
    def delete(self, id: int)

class ModelRepository(BaseRepository):
    def get_by_name(self, name: str)
    def search(self, query: str)
    # domain-specific methods
```

**Best Practices:**

- Repository pattern (decouples data access from business logic)
- Context managers for sessions
- Type hints throughout
- Comprehensive docstrings

**Testing:**

- Unit tests for each repository method
- Test fixtures for sample data
- Integration tests with test database

---

## **Phase 2: API Layer with FastAPI**

### **Module 2.1: Pydantic Schemas & API Foundation**

**Duration:** 2 hours  
**Learning Goals:** Request/response validation, API design, OpenAPI docs

**What you'll build:**

- Pydantic schemas for all entities (Create, Update, Response)
- FastAPI application structure with routers
- Health check and basic endpoints
- Automatic API documentation

**Schema Pattern:**

```python
# Input/Output separation
class ModelCreate(BaseModel):     # For POST requests
class ModelUpdate(BaseModel):     # For PUT/PATCH
class ModelResponse(BaseModel):   # For responses
    class Config:
        from_attributes = True    # ORM compatibility
```

**Best Practices:**

- Input validation with Pydantic
- Separate schemas for different operations
- Response models for consistent API
- Proper HTTP status codes
- API versioning from the start (/api/v1/)

**Testing:**

- API endpoint tests with TestClient
- Schema validation tests
- Status code verification

---

### **Module 2.2: CRUD Endpoints & Error Handling**

**Duration:** 3 hours  
**Learning Goals:** RESTful API design, error handling, dependency injection

**What you'll build:**

- Complete CRUD endpoints for models, benchmarks, results
- Custom exception handlers
- Dependency injection for database sessions
- Query parameters for filtering/pagination

**API Routes:**

```
GET    /api/v1/models              # List with pagination
POST   /api/v1/models              # Create
GET    /api/v1/models/{id}         # Get one
PUT    /api/v1/models/{id}         # Update
DELETE /api/v1/models/{id}         # Delete
GET    /api/v1/models/{id}/benchmarks  # Related data
GET    /api/v1/models/search?q=...     # Search
```

**Best Practices:**

- RESTful conventions
- Proper error responses with details
- Request/response logging
- Pagination for list endpoints
- CORS configuration

**Testing:**

- Full endpoint test coverage
- Error case testing
- Edge case validation

---

## **Phase 3: LLM-Powered Manual Input**

### **Module 3.1: LLM Service Layer**

**Duration:** 2 hours  
**Learning Goals:** API integration, prompt engineering, structured extraction

**What you'll build:**

- Abstract LLM service (supports multiple providers)
- Anthropic Claude integration
- Prompt templates for extraction
- Structured output parsing

**Service Pattern:**

```python
class LLMService:
    def extract_model_info(self, text: str) -> ModelExtraction
    def extract_benchmark_results(self, text: str) -> List[BenchmarkResult]
    def extract_opinions(self, text: str) -> List[Opinion]

# With proper error handling, retries, rate limiting
```

**Best Practices:**

- Prompt templates as configuration
- Structured output with JSON mode
- Error handling for API failures
- Response caching for development
- Cost tracking/logging

**Testing:**

- Mock LLM responses for tests
- Prompt validation tests
- Integration tests with real API (marked as slow)

---

### **Module 3.2: Manual Input Endpoint & Processing Pipeline**

**Duration:** 2 hours  
**Learning Goals:** Async processing, data validation, pipeline pattern

**What you'll build:**

- POST endpoint for text submission
- Processing pipeline: extract → validate → store
- Confidence scoring for extracted data
- Manual review/approval workflow (optional)

**Pipeline Architecture:**

```python
TextInput → LLM Extraction → Validation → Database Storage
         ↓
    Processing Status & Logs
```

**Best Practices:**

- Async/await for LLM calls
- Background tasks for long operations
- Status tracking for user feedback
- Idempotency for retries

**Testing:**

- End-to-end pipeline tests
- Various input formats
- Error recovery scenarios

---

## **Phase 4: RSS Newsletter Ingestion**

### **Module 4.1: RSS Feed Parser & Scheduler**

**Duration:** 2 hours  
**Learning Goals:** Feed parsing, scheduling, background jobs

**What you'll build:**

- RSS feed parser with feedparser
- APScheduler integration
- Newsletter item storage (before processing)
- Deduplication logic

**Scheduler Pattern:**

```python
# Runs Monday-Friday at 9 AM
@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=9)
def fetch_newsletter():
    # Fetch → Parse → Store for processing
```

**Best Practices:**

- Graceful failure handling
- Job monitoring/logging
- Prevent duplicate processing
- Configurable schedule

**Testing:**

- Parser tests with sample RSS
- Scheduler mock tests
- Deduplication tests

---

### **Module 4.2: Automated Content Extraction Pipeline**

**Duration:** 3 hours  
**Learning Goals:** Batch processing, data pipeline, monitoring

**What you'll build:**

- Batch processor for newsletter items
- Context-aware LLM extraction (newsletter format specific)
- Automated database updates
- Processing reports/notifications

**Pipeline:**

```python
RSS Items → Batch → LLM Extraction → Validation → Database
         ↓
    Process Logs & Metrics
```

**Best Practices:**

- Batch processing for efficiency
- Transaction management for consistency
- Retry logic for failures
- Comprehensive logging
- Metrics collection (items processed, errors, etc.)

**Testing:**

- Full pipeline integration tests
- Failure scenario tests
- Performance tests

---

## **Phase 5: Frontend Application**

### **Module 5.1: React Setup & Component Architecture**

**Duration:** 2 hours  
**Learning Goals:** Modern React setup, component patterns, state management

**What you'll build:**

- Vite + React + TypeScript setup
- shadcn/ui integration
- Component structure and routing
- API client setup with TanStack Query

**Component Structure:**

```
src/
├── components/
│   ├── ui/              # shadcn components
│   ├── layout/          # Layout components
│   └── features/        # Feature components
├── pages/               # Route pages
├── lib/                 # Utilities
├── hooks/               # Custom hooks
└── api/                 # API client
```

**Best Practices:**

- Component composition
- Custom hooks for logic reuse
- TypeScript for type safety
- Proper file organization

---

### **Module 5.2: Model Catalogue UI**

**Duration:** 3 hours  
**Learning Goals:** Data fetching, tables, filtering, responsive design

**What you'll build:**

- Model list view with filtering/sorting
- Model detail page with benchmark visualization
- Search functionality
- Responsive design with Tailwind

**Best Practices:**

- Loading states
- Error boundaries
- Optimistic updates
- Accessible components

---

### **Module 5.3: Manual Input Interface**

**Duration:** 2 hours  
**Learning Goals:** Forms, validation, async operations

**What you'll build:**

- Text input form with rich editor
- Processing status display
- Result preview before confirmation
- Error handling UI

**Best Practices:**

- Client-side validation
- Form state management
- User feedback (loading, success, errors)
- Progressive enhancement

---

## **Phase 6: Deployment & Operations**

### **Module 6.1: Docker Configuration**

**Duration:** 2 hours  
**Learning Goals:** Docker, multi-stage builds, docker-compose

**What you'll build:**

- Optimized Dockerfiles for backend/frontend
- Docker Compose orchestration
- Volume management for persistence
- Environment configuration

**Best Practices:**

- Multi-stage builds (smaller images)
- Layer caching optimization
- Security hardening
- Health checks

---

### **Module 6.2: Production Deployment**

**Duration:** 3 hours  
**Learning Goals:** VPS deployment, SSL, monitoring, backups

**What you'll build:**

- Deployment script
- Nginx/Caddy reverse proxy
- SSL with Let's Encrypt
- Database backup strategy
- Basic monitoring/logging

**Best Practices:**

- Zero-downtime deployments
- Automated backups
- Log aggregation
- Security hardening (firewall, secrets management)

---

### **Module 6.3: Maintenance & Monitoring**

**Duration:** 1 hour  
**Learning Goals:** Production operations, debugging

**What you'll build:**

- Health check endpoints
- Logging strategy
- Error tracking
- Update procedures

---

## **Appendix: Cross-Cutting Concepts**

Throughout all modules, you'll learn:

- **Git Workflow:** Feature branches, conventional commits, PR reviews
- **Testing Pyramid:** Unit → Integration → E2E
- **Documentation:** Code comments, API docs, README
- **Security:** Input validation, SQL injection prevention, secrets management
- **Performance:** Database indexing, caching, query optimization
- **Code Quality:** Linting, formatting, type checking

---

## **Estimated Timeline**

- **Part-time (5-10 hours/week):** 6-8 weeks
- **Full-time focus:** 2-3 weeks
