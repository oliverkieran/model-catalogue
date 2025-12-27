# Module 3.1: Architecture Diagrams

## LLM Service Integration Architecture

### High-Level System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     User / Frontend                         │
└────────────────────────────┬────────────────────────────────┘
                             │ POST /api/v1/extract
                             │ { "text": "GPT-4..." }
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Application                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Endpoint (/api/v1/extract)                      │   │
│  │  - Receives text input                               │   │
│  │  - Validates request                                 │   │
│  │  - Returns extracted model data                      │   │
│  └───────────────────────┬──────────────────────────────┘   │
│                          │ Depends(get_llm_service)         │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LLMService (Business Logic)                         │   │
│  │  - Formats prompts                                   │   │
│  │  - Calls Claude API                                  │   │
│  │  - Validates responses                               │   │
│  │  - Handles retries                                   │   │
│  └───────────────────────┬──────────────────────────────┘   │
│                          │ anthropic.AsyncAnthropic         │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Anthropic SDK                                       │   │
│  │  - HTTP client                                       │   │
│  │  - Authentication                                    │   │
│  │  - Request/response handling                         │   │
│  └───────────────────────┬──────────────────────────────┘   │
└──────────────────────────┼──────────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Claude API (Anthropic Cloud)                   │
│  - Processes prompt                                         │
│  - Executes extraction                                      │
│  - Returns structured data                                  │
└─────────────────────────────────────────────────────────────┘
```

### Service Layer Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    Architecture Layers                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────┐     │
│  │  API Layer (app/api/)                             │     │
│  │  - HTTP request/response handling                 │     │
│  │  - Route definitions                              │     │
│  │  - FastAPI decorators                             │     │
│  └────────────────────┬──────────────────────────────┘     │
│                       │ Depends()                          │
│                       ▼                                     │
│  ┌───────────────────────────────────────────────────┐     │
│  │  Service Layer (app/services/)                    │     │
│  │  - Business logic                                 │     │
│  │  - LLM interactions                               │     │
│  │  - Data transformation                            │     │
│  │  - External API calls                             │     │
│  └────────────────────┬──────────────────────────────┘     │
│                       │ Uses                               │
│                       ▼                                     │
│  ┌───────────────────────────────────────────────────┐     │
│  │  Repository Layer (app/db/repositories/)          │     │
│  │  - Database operations                            │     │
│  │  - Query building                                 │     │
│  │  - Transaction management                         │     │
│  └────────────────────┬──────────────────────────────┘     │
│                       │ SQLModel                           │
│                       ▼                                     │
│  ┌───────────────────────────────────────────────────┐     │
│  │  Database (Supabase PostgreSQL)                   │     │
│  │  - Data persistence                               │     │
│  │  - Constraints & indexes                          │     │
│  └───────────────────────────────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### LLM Extraction Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: User provides text                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ "OpenAI released GPT-4 in March 2023. It's a large   │  │
│  │  multimodal model with 8K context window."           │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: LLMService formats prompt                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ System Prompt:                                        │  │
│  │ "You are a data extraction assistant..."             │  │
│  │ [Examples with <example> tags]                       │  │
│  │                                                       │  │
│  │ User Message:                                         │  │
│  │ "Extract model information from: [text]"             │  │
│  │                                                       │  │
│  │ Tool Definition:                                      │  │
│  │ { "name": "extract_model", "strict": true, ... }     │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Call Claude API with retry logic                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Try 1: Send request                                   │  │
│  │   ├─ Success → Return response                        │  │
│  │   └─ RateLimitError → Wait 1s, retry                  │  │
│  │                                                        │  │
│  │ Try 2: Send request                                   │  │
│  │   ├─ Success → Return response                        │  │
│  │   └─ InternalServerError → Wait 2s, retry            │  │
│  │                                                        │  │
│  │ Try 3: Send request                                   │  │
│  │   ├─ Success → Return response                        │  │
│  │   └─ Error → Raise exception                          │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Claude processes and returns structured data       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Tool Use Response:                                    │  │
│  │ {                                                     │  │
│  │   "model_name": "gpt-4",                              │  │
│  │   "display_name": "GPT-4",                            │  │
│  │   "organization": "OpenAI",                           │  │
│  │   "release_date": "2023-03-01",                       │  │
│  │   "description": "A large multimodal model",          │  │
│  │   "metadata_": {"context_window": 8192}               │  │
│  │ }                                                     │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Validate with Pydantic schema                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ ExtractedModel(**response_data)                       │  │
│  │  ✓ model_name is valid string                        │  │
│  │  ✓ release_date is valid ISO date                    │  │
│  │  ✓ metadata_ is valid dict                           │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 6: Return ExtractionResult                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ ExtractionResult(                                     │  │
│  │   data=ExtractedModel(...),                           │  │
│  │   tokens_used=1847,                                   │  │
│  │   model_used="claude-sonnet-4-5-20250929"             │  │
│  │ )                                                     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Prompt Caching Mechanism

```
┌─────────────────────────────────────────────────────────────┐
│  First Call (use_cache=True)                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Request:                                                   │
│  ┌────────────────────────────────────────────────┐        │
│  │ System Prompt (1500 tokens)                    │        │
│  │ + cache_control: {"type": "ephemeral"}         │ ◄──────┼── Cached
│  │                                                 │        │
│  │ User Message: "Extract from: [text]"           │        │
│  └────────────────────────────────────────────────┘        │
│                                                             │
│  Cost: ~1850 tokens (500 input + 1500 cache_creation + ... │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                             │
                             │ 5 minutes later...
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Second Call (use_cache=True)                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Request:                                                   │
│  ┌────────────────────────────────────────────────┐        │
│  │ System Prompt (1500 tokens)                    │        │
│  │ + cache_control: {"type": "ephemeral"}         │ ◄──────┼── Read from cache
│  │                                   [CACHED] ✓   │        │   (90% discount)
│  │                                                 │        │
│  │ User Message: "Extract from: [different text]" │        │
│  └────────────────────────────────────────────────┘        │
│                                                             │
│  Cost: ~650 tokens (500 input + 150 cache_read)            │
│  Savings: ~1200 tokens (65% reduction)                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Error Handling & Retry Flow

```
┌─────────────────────────────────────────────────────────────┐
│  API Call with Exponential Backoff                          │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │  Attempt 1 (immediate)   │
              └──────────┬───────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼ Success                       ▼ Rate Limit (429)
    ┌─────────┐                    ┌──────────────────┐
    │ Return  │                    │  Wait 1 second   │
    │Response │                    └────────┬─────────┘
    └─────────┘                             │
                                            ▼
                              ┌──────────────────────────┐
                              │  Attempt 2 (after 1s)    │
                              └──────────┬───────────────┘
                                         │
                         ┌───────────────┴───────────────┐
                         │                               │
                         ▼ Success                       ▼ Server Error (500)
                    ┌─────────┐                    ┌──────────────────┐
                    │ Return  │                    │  Wait 2 seconds  │
                    │Response │                    └────────┬─────────┘
                    └─────────┘                             │
                                                            ▼
                                              ┌──────────────────────────┐
                                              │  Attempt 3 (after 2s)    │
                                              └──────────┬───────────────┘
                                                         │
                                         ┌───────────────┴───────────────┐
                                         │                               │
                                         ▼ Success                       ▼ Connection Error
                                    ┌─────────┐                    ┌──────────────────┐
                                    │ Return  │                    │  Wait 4 seconds  │
                                    │Response │                    └────────┬─────────┘
                                    └─────────┘                             │
                                                                            ▼
                                                              ┌──────────────────────────┐
                                                              │  Attempt 4 (after 4s)    │
                                                              │  Max retries exhausted   │
                                                              └──────────┬───────────────┘
                                                                         │
                                                                         ▼
                                                                   ┌──────────┐
                                                                   │  Raise   │
                                                                   │  Error   │
                                                                   └──────────┘

Retryable Errors:                    Non-Retryable Errors:
- 429 Rate Limit                     - 400 Bad Request
- 500-599 Server Errors              - 401 Unauthorized
- Connection Errors                  - 403 Forbidden
                                     - 404 Not Found
```

### Testing Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                     Testing Pyramid                         │
└─────────────────────────────────────────────────────────────┘

                        ▲
                       ╱ ╲
                      ╱   ╲              E2E Tests (Slow)
                     ╱─────╲             - Real Claude API
                    ╱       ╲            - Full extraction pipeline
                   ╱─────────╲           - Marked with @pytest.mark.slow
                  ╱           ╲          - Run manually (~$0.01/run)
                 ╱─────────────╲         - 1 test
                ╱               ╲
               ╱─────────────────╲       Integration Tests (Fast)
              ╱                   ╲      - Mocked Claude responses
             ╱─────────────────────╲     - Test service + validation
            ╱                       ╲    - 6 tests
           ╱─────────────────────────╲
          ╱                           ╲  Unit Tests (Fastest)
         ╱─────────────────────────────╲ - Initialization
        ╱_____________________________ ╲ - Error handling
                                         - Retry logic
                                         - Cache configuration
                                         - 8 tests

┌─────────────────────────────────────────────────────────────┐
│  Test Execution                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Default (CI/CD):                                           │
│  $ pytest                                                   │
│  → Runs unit + integration (mocked)                         │
│  → Fast (<1 second)                                         │
│  → Free (no API calls)                                      │
│                                                             │
│  Manual (Development):                                      │
│  $ pytest -m slow                                           │
│  → Runs E2E tests with real API                            │
│  → Slow (~5-10 seconds)                                     │
│  → Costs ~$0.01                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow: Text to Database

```
┌──────────────────────────────────────────────────────────────┐
│  User Input (Unstructured Text)                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ "OpenAI's GPT-4, released in March 2023, is a large   │  │
│  │  multimodal model with an 8K context window."         │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  LLM Extraction (Structured Output)                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ExtractedModel(                                        │  │
│  │   model_name="gpt-4",                                  │  │
│  │   display_name="GPT-4",                                │  │
│  │   organization="OpenAI",                               │  │
│  │   release_date=date(2023, 3, 1),                       │  │
│  │   description="A large multimodal model",              │  │
│  │   metadata_={"context_window": 8192}                   │  │
│  │ )                                                      │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Validation (Pydantic Schema)                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ✓ model_name: non-empty string                         │  │
│  │ ✓ organization: non-empty string                       │  │
│  │ ✓ release_date: valid ISO date                         │  │
│  │ ✓ metadata_: valid JSON object                         │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Transformation (ExtractedModel → ModelCreate)               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ModelCreate(                                           │  │
│  │   name="gpt-4",           # Maps from model_name       │  │
│  │   display_name="GPT-4",                                │  │
│  │   organization="OpenAI",                               │  │
│  │   release_date=date(2023, 3, 1),                       │  │
│  │   description="A large multimodal model",              │  │
│  │   metadata_={"context_window": 8192}                   │  │
│  │ )                                                      │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  Database Insertion (Repository Layer)                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Model(                                                 │  │
│  │   id=1,                          # Auto-generated      │  │
│  │   name="gpt-4",                                        │  │
│  │   display_name="GPT-4",                                │  │
│  │   organization="OpenAI",                               │  │
│  │   release_date=date(2023, 3, 1),                       │  │
│  │   description="A large multimodal model",              │  │
│  │   metadata_={"context_window": 8192},                  │  │
│  │   created_at=datetime.now(),     # Auto-generated      │  │
│  │   updated_at=None                                      │  │
│  │ )                                                      │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Key Architectural Principles

### 1. Separation of Concerns

```
┌────────────────────────────────────────────┐
│  API Layer         → HTTP handling         │
│  Service Layer     → Business logic        │
│  Repository Layer  → Data access           │
│  Database          → Persistence           │
└────────────────────────────────────────────┘
```

### 2. Dependency Injection

```python
# FastAPI automatically injects dependencies
@router.post("/extract")
async def extract_model(
    llm_service: LLMService = Depends(get_llm_service),  # ← Injected
    session: AsyncSession = Depends(get_db)              # ← Injected
):
    result = await llm_service.extract_model_data(text)
    # ...
```

### 3. Fail-Safe Design

```
┌─────────────────────────────────────────┐
│  Every layer has error handling:       │
├─────────────────────────────────────────┤
│  API         → HTTPException            │
│  Service     → Retry logic              │
│  Repository  → Transaction rollback     │
│  Validation  → Pydantic errors          │
└─────────────────────────────────────────┘
```

### 4. Cost Optimization

```
┌─────────────────────────────────────────┐
│  Caching Strategy:                      │
├─────────────────────────────────────────┤
│  System Prompt     → Cached (1500 tok)  │
│  Examples          → Cached (included)  │
│  User Message      → Not cached         │
│                                         │
│  First call:  1850 tokens ($0.005)      │
│  Later calls:  650 tokens ($0.002)      │
│  Savings:      65% per call             │
└─────────────────────────────────────────┘
```
