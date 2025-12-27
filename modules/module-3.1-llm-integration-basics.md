# Module 3.1: LLM Integration Basics - Teaching Your API to Understand Text

**Duration:** 3-4 hours
**Difficulty:** Intermediate-Advanced
**Prerequisites:** Modules 0-2.2 complete (database, repositories, CRUD APIs)

---

## Overview

You've built a solid CRUD API for managing AI models, benchmarks, and results. But there's a problem: entering data manually is tedious. Imagine copying benchmark results from a research paper - you need to find the model name, extract the score, identify the benchmark, and carefully type it all into your API.

**What if your API could read the text and extract this information automatically?**

That's exactly what we'll build in this module using **Claude**, Anthropic's large language model. By the end, you'll have an LLM-powered service that can read arbitrary text like this:

```text
"GPT-4 scored 86.5% on MMLU in March 2023, according to OpenAI's technical report."
```

And automatically extract structured data:

```json
{
  "model_name": "gpt-4",
  "organization": "OpenAI",
  "benchmark_name": "MMLU",
  "score": 86.5,
  "date_tested": "2023-03-01",
  "source": "OpenAI technical report"
}
```

This isn't just a cool feature - it's the foundation for **automated data ingestion** (Module 4) where your API will process RSS feeds and news articles automatically. More importantly, you'll learn professional LLM integration patterns that transfer to any AI-powered application.

## Learning Objectives

By the end of this module, you will be able to:

1. **Integrate the Claude API** into a FastAPI application using the official Anthropic Python SDK
2. **Engineer effective prompts** following Claude 4.5 best practices (explicit instructions, context, examples, structured outputs)
3. **Implement the Service Layer pattern** for LLM interactions that separates business logic from API routes
4. **Use Structured Outputs** with strict schemas to guarantee valid JSON responses from Claude
5. **Optimize costs** with prompt caching to reduce API expenses during development
6. **Build robust error handling** with retry logic and exponential backoff for rate limits
7. **Validate LLM outputs** against your SQLModel schemas before database insertion
8. **Test LLM integrations** effectively using mocked responses to avoid API costs

## Prerequisites

Before starting, ensure you have:

- Completed Modules 0-2.2 (repository pattern, CRUD APIs, error handling)
- An **Anthropic API key** (get one free at https://console.anthropic.com)
- Basic understanding of async/await in Python
- Familiarity with Pydantic/SQLModel schemas

**Getting Your Claude API Key:**

1. Visit https://console.anthropic.com and create an account
2. Navigate to "API Keys" in the settings
3. Click "Create Key" and copy the key (starts with `sk-ant-`)
4. Add to your `.env` file: `ANTHROPIC_API_KEY=sk-ant-...`

Don't worry about costs - this module's examples use ~$0.05 worth of API calls, and Anthropic provides $5 free credit.

---

## Conceptual Foundation

### The Problem: Manual Data Entry is a Bottleneck

Consider your Model Catalogue API. Right now, adding benchmark results requires manual extraction:

1. Read a research paper: "On MMLU, GPT-4 achieved 86.5%..."
2. Manually identify: model=GPT-4, benchmark=MMLU, score=86.5
3. Find IDs in your database: model_id=1, benchmark_id=5
4. Make POST request: `{"model_id": 1, "benchmark_id": 5, "score": 86.5}`

This works for 10 results. But what about 1,000 results from multiple papers? Or daily updates from AI newsletters? **Manual entry doesn't scale.**

### The Solution: LLM-Powered Extraction

Large Language Models like Claude excel at understanding unstructured text and extracting structured information. Instead of manual entry, you can:

1. Paste arbitrary text from any source
2. Claude reads and understands the content
3. Claude extracts structured data matching your database schema
4. You validate and insert into the database

**The key insight:** LLMs bridge the gap between human-readable text and machine-readable data.

### Why Claude?

There are many LLMs available (OpenAI's GPT, Google's Gemini, open-source models). We chose **Claude** because:

1. **Structured Outputs with `strict: true`** - Guaranteed schema conformance (no invalid JSON)
2. **Strong instruction following** - Claude excels at precise extraction tasks
3. **Prompt caching** - Reduce costs by caching system prompts and examples
4. **Long context windows** - Handle long documents (200K+ tokens)
5. **Excellent developer experience** - Clean API, comprehensive docs

**Available Claude Models (as of January 2025):**

- **Claude Sonnet 4.5** (`claude-sonnet-4-5-20250929`) - Best for complex extraction (recommended for this module)
- **Claude Haiku 4.5** (`claude-haiku-4-5-20250929`) - Faster, cheaper for simple tasks
- **Claude Opus 4.5** (`claude-opus-4-5-20250929`) - Most capable for very complex reasoning

For our extraction task, **Sonnet 4.5** offers the best balance of accuracy and cost.

### Industry Context: The Service Layer Pattern

Before writing code, we need to discuss **architecture**. Where does LLM code live in your application?

**Bad approach:** Put LLM calls directly in API endpoints

```python
# ❌ Don't do this - business logic mixed with HTTP handling
@router.post("/extract")
async def extract_data(text: str):
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    response = await client.messages.create(...)
    # Extraction logic, validation, etc.
    return response
```

**Problems:**
- Can't reuse extraction logic in other endpoints
- Difficult to test (need to mock HTTP requests)
- Violates Single Responsibility Principle (endpoint does HTTP *and* LLM *and* validation)
- Can't swap LLM providers without changing every endpoint

**Professional approach:** Create a **Service Layer**

```python
# ✅ Service layer separates business logic
class LLMService:
    """Handles all Claude API interactions"""

    async def extract_model_data(self, text: str) -> dict:
        """Extract model information from text"""
        # LLM logic here

# API endpoint delegates to service
@router.post("/extract")
async def extract_data(text: str, llm_service: LLMService = Depends()):
    return await llm_service.extract_model_data(text)
```

**Benefits:**
- **Separation of Concerns:** Services handle business logic, endpoints handle HTTP
- **Reusability:** Use `LLMService` in multiple endpoints, scheduled jobs, CLI scripts
- **Testability:** Mock services easily in tests
- **Maintainability:** Change LLM provider in one place
- **Dependency Injection:** FastAPI provides services via `Depends()`

This mirrors the **Repository Pattern** from Module 1.2 - repositories handle data access, services handle business logic.

---

## Implementation Guide

### Architecture Overview

We'll build this in layers:

```
┌─────────────────────────────────────────────┐
│  API Endpoint (/api/v1/extract)             │
│  - Receives text input                      │
│  - Returns extracted data                   │
└────────────┬────────────────────────────────┘
             │ delegates to
             ▼
┌─────────────────────────────────────────────┐
│  LLMService (app/services/llm_service.py)   │
│  - Formats prompts                          │
│  - Calls Claude API                         │
│  - Validates responses                      │
└────────────┬────────────────────────────────┘
             │ uses
             ▼
┌─────────────────────────────────────────────┐
│  Anthropic SDK (anthropic.AsyncAnthropic)   │
│  - Manages API calls                        │
│  - Handles authentication                   │
└─────────────────────────────────────────────┘
```

Let's build this step by step, starting with dependencies.

### Step 1: Install Dependencies

The Anthropic SDK is already in your `pyproject.toml`:

```toml
dependencies = [
    "anthropic>=0.75.0",  # ✅ Already installed
    # ... other dependencies
]
```

If you need to install it manually:

```bash
cd backend
uv add anthropic
```

### Step 2: Configure API Key

Your `config.py` already has the configuration:

```python
class Settings(BaseSettings):
    # LLM Service
    anthropic_api_key: str = ""  # ✅ Already configured
```

Add your API key to `.env`:

```bash
# Add this line to backend/.env
ANTHROPIC_API_KEY=sk-ant-api03-...your-key-here...
```

**Security note:** Never commit API keys to git. The `.env` file is gitignored by default.

### Step 3: Create the LLM Service

Create a new file for the LLM service:

**File:** `backend/app/services/llm_service.py`

```python
"""
LLM Service for Claude API Integration

This service handles all interactions with Claude (Anthropic's LLM),
including data extraction, prompt engineering, and response validation.
"""

import logging
from typing import Any
from anthropic import AsyncAnthropic
from anthropic.types import Message
from pydantic import BaseModel, ValidationError

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for interacting with Claude API.

    Handles prompt engineering, structured extraction, caching,
    and error handling for LLM-powered features.
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize the LLM service with Claude API client.

        Args:
            api_key: Anthropic API key. If None, uses settings.anthropic_api_key
        """
        self.api_key = api_key or settings.anthropic_api_key
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not configured. Set ANTHROPIC_API_KEY in .env"
            )

        # Initialize async client
        self.client = AsyncAnthropic(api_key=self.api_key)

        # Default model - Sonnet 4.5 for complex extraction
        self.model = "claude-sonnet-4-5-20250929"

    async def close(self):
        """Close the API client. Call this in cleanup/shutdown."""
        await self.client.close()
```

**What's happening here?**

1. **Dependency on settings:** Uses `settings.anthropic_api_key` from configuration
2. **AsyncAnthropic client:** Async client for non-blocking API calls (important for FastAPI)
3. **Model selection:** Defaults to Sonnet 4.5 (best for our extraction task)
4. **Error handling:** Raises clear error if API key is missing
5. **Resource cleanup:** `close()` method for proper cleanup (we'll use this later)

**Why `api_key` parameter?** It allows dependency injection in tests:

```python
# Production: uses settings.anthropic_api_key
service = LLMService()

# Testing: inject mock key or custom key
service = LLMService(api_key="test-key")
```

### Step 4: Understanding Claude's Message API

Before building extraction, let's understand how Claude's API works. Here's the basic structure:

```python
response = await client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Extract the model name from: GPT-4 scored 86.5% on MMLU"
        }
    ]
)

# Response structure
print(response.content[0].text)  # "The model name is GPT-4"
```

**Key concepts:**

1. **Messages:** Conversation turns with roles (`user`, `assistant`)
2. **System prompts:** Special instructions that guide Claude's behavior (added separately)
3. **max_tokens:** Maximum response length (controls cost)
4. **Response format:** Claude returns a `Message` object with `content` array

For **structured extraction**, we use **tool use** (function calling):

```python
# Define the schema you want Claude to return
tools = [{
    "name": "extract_model",
    "description": "Extract model information from text",
    "input_schema": {
        "type": "object",
        "properties": {
            "model_name": {"type": "string"},
            "score": {"type": "number"}
        },
        "required": ["model_name"]
    }
}]

response = await client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "GPT-4 scored 86.5%"}]
)

# Claude returns structured data matching your schema
tool_use = response.content[0]
data = tool_use.input  # {"model_name": "gpt-4", "score": 86.5}
```

**Important:** With `strict: true` (added in December 2024), Claude **guarantees** the response matches your schema. No more parsing errors!

### Step 5: Prompt Engineering for Extraction

Effective prompts are critical. Let's build a prompt for extracting AI model information.

**Claude 4.5 Best Practices:**

1. **Be explicit and clear:** State exactly what to extract
2. **Provide context:** Explain *why* you need this data
3. **Give 3-5 diverse examples:** Cover edge cases
4. **Use structured formats:** XML tags, JSON schemas
5. **Positive framing:** "Do X" not "Don't do Y"

**Bad prompt (vague, no examples):**

```python
prompt = "Extract model information from this text."
```

**Good prompt (explicit, with context and examples):**

```python
SYSTEM_PROMPT = """You are a data extraction assistant for an AI Model Catalogue database.

Your task is to extract information about AI models from unstructured text sources like:
- Research papers
- Technical blog posts
- News articles
- Benchmark reports

Extract the following fields:
- model_name: The technical identifier (e.g., "gpt-4", "claude-3-sonnet")
- display_name: Human-readable name (e.g., "GPT-4", "Claude 3 Sonnet")
- organization: The company/institution that created it
- release_date: When it was released (ISO format YYYY-MM-DD)
- description: Brief description of the model's purpose/capabilities
- license: License type if mentioned (e.g., "Apache 2.0", "Proprietary")

Important guidelines:
- Only extract information explicitly stated in the text
- Use null for missing fields rather than guessing
- Normalize model names to lowercase with hyphens (gpt-4, not GPT4)
- Infer release_date from context clues ("in March 2023" → "2023-03-01")
- Keep descriptions concise (1-2 sentences)

Examples:

<example>
Input: "OpenAI released GPT-4 in March 2023. GPT-4 is a large multimodal model capable of processing both text and images."
Output:
{
  "model_name": "gpt-4",
  "display_name": "GPT-4",
  "organization": "OpenAI",
  "release_date": "2023-03-01",
  "description": "A large multimodal model capable of processing both text and images",
  "license": null
}
</example>

<example>
Input: "Anthropic's Claude 3.5 Sonnet, released June 2024, is licensed under a proprietary license."
Output:
{
  "model_name": "claude-3.5-sonnet",
  "display_name": "Claude 3.5 Sonnet",
  "organization": "Anthropic",
  "release_date": "2024-06-01",
  "description": null,
  "license": "Proprietary"
}
</example>

<example>
Input: "LLaMA 2 was open-sourced by Meta in 2023 with improved performance."
Output:
{
  "model_name": "llama-2",
  "display_name": "LLaMA 2",
  "organization": "Meta",
  "release_date": "2023-01-01",
  "description": "Open-source model with improved performance",
  "license": "Open Source"
}
</example>

<example>
Input: "This model is amazing!"
Output: null
(No extractable model information - text is too vague)
</example>

Now extract model information from the text provided by the user.
"""
```

**What makes this prompt effective?**

1. **Role and context:** "You are a data extraction assistant for an AI Model Catalogue"
2. **Explicit field definitions:** Each field has a description and example format
3. **Clear guidelines:** Normalize names, use null for missing data, infer dates
4. **Diverse examples:** Cover standard cases, missing fields, and invalid input
5. **XML structure:** `<example>` tags make examples clear
6. **Positive framing:** "Use null for missing fields" vs "Don't make up data"

### Step 6: Define Extraction Schema

We need a Pydantic schema that matches our SQLModel `ModelCreate` schema. This ensures extracted data can be validated before database insertion.

Add to `llm_service.py`:

```python
from datetime import date
from pydantic import BaseModel, Field


class ExtractedModel(BaseModel):
    """
    Schema for AI model data extracted by LLM.

    Matches ModelCreate but all fields are optional since
    extraction may not find complete information.
    """
    model_name: str | None = Field(
        None,
        description="Technical model identifier (lowercase with hyphens)",
        examples=["gpt-4", "claude-3-sonnet", "llama-2"]
    )
    display_name: str | None = Field(
        None,
        description="Human-readable model name",
        examples=["GPT-4", "Claude 3 Sonnet", "LLaMA 2"]
    )
    organization: str | None = Field(
        None,
        description="Organization that created the model",
        examples=["OpenAI", "Anthropic", "Meta"]
    )
    release_date: date | None = Field(
        None,
        description="Release date in ISO format (YYYY-MM-DD)"
    )
    description: str | None = Field(
        None,
        description="Brief description of model capabilities"
    )
    license: str | None = Field(
        None,
        description="License type",
        examples=["Apache 2.0", "MIT", "Proprietary", "Open Source"]
    )
    metadata_: dict | None = Field(
        None,
        description="Additional metadata (context window, pricing, etc.)"
    )


class ExtractionResult(BaseModel):
    """
    Result of an LLM extraction operation.

    Contains the extracted data plus metadata about the extraction
    (tokens used, model, extraction confidence, etc.)
    """
    data: ExtractedModel | None = Field(
        None,
        description="Extracted model data, or None if no data could be extracted"
    )
    tokens_used: int = Field(
        description="Total tokens used in the extraction"
    )
    model_used: str = Field(
        description="Claude model used for extraction"
    )
```

**Design decisions:**

1. **All fields optional:** Extraction may not find all fields
2. **Field descriptions:** Used in the tool schema sent to Claude
3. **ExtractionResult wrapper:** Includes metadata for monitoring/debugging
4. **Matches ModelCreate:** Can easily convert to database schema

### Step 7: Implement Extraction Method

Now let's implement the actual extraction logic. Add to `LLMService`:

```python
from anthropic import AsyncAnthropic
from anthropic.types import ToolParam


class LLMService:
    # ... __init__ method from Step 3 ...

    async def extract_model_data(
        self,
        text: str,
        use_cache: bool = True
    ) -> ExtractionResult:
        """
        Extract AI model information from unstructured text.

        Uses Claude with structured outputs (strict mode) to guarantee
        valid JSON responses matching the ExtractedModel schema.

        Args:
            text: The text to extract model information from
            use_cache: Enable prompt caching to reduce costs (default: True)

        Returns:
            ExtractionResult with extracted data and token usage

        Raises:
            ValueError: If text is empty
            anthropic.APIError: If the API call fails after retries
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Define the extraction tool with strict schema
        extract_tool: ToolParam = {
            "name": "extract_model",
            "description": "Extract AI model information from text",
            "input_schema": {
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": ["string", "null"],
                        "description": "Technical model identifier (lowercase with hyphens)"
                    },
                    "display_name": {
                        "type": ["string", "null"],
                        "description": "Human-readable model name"
                    },
                    "organization": {
                        "type": ["string", "null"],
                        "description": "Organization that created the model"
                    },
                    "release_date": {
                        "type": ["string", "null"],
                        "description": "Release date in ISO format (YYYY-MM-DD)",
                        "format": "date"
                    },
                    "description": {
                        "type": ["string", "null"],
                        "description": "Brief description of model capabilities"
                    },
                    "license": {
                        "type": ["string", "null"],
                        "description": "License type"
                    },
                    "metadata_": {
                        "type": ["object", "null"],
                        "description": "Additional metadata"
                    }
                },
                "required": []  # All fields optional
            },
            "strict": True  # ✨ Strict mode guarantees schema conformance
        }

        # Build system prompt with caching
        system_blocks = [
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                # Cache this block to reduce costs on repeated calls
                "cache_control": {"type": "ephemeral"} if use_cache else None
            }
        ]
        # Remove None cache_control if not using cache
        if not use_cache:
            system_blocks[0].pop("cache_control", None)

        # Call Claude with retry logic
        try:
            response = await self._call_claude_with_retry(
                system=system_blocks,
                messages=[
                    {
                        "role": "user",
                        "content": f"Extract model information from this text:\n\n{text}"
                    }
                ],
                tools=[extract_tool],
                tool_choice={"type": "tool", "name": "extract_model"}
            )
        except Exception as e:
            logger.error(f"Failed to extract model data: {e}")
            raise

        # Extract the tool use from response
        extracted_data = None
        for content_block in response.content:
            if content_block.type == "tool_use" and content_block.name == "extract_model":
                # Claude returns the data in content_block.input
                raw_data = content_block.input

                # Validate against our Pydantic schema
                try:
                    extracted_data = ExtractedModel(**raw_data)
                except ValidationError as e:
                    logger.error(f"Extracted data failed validation: {e}")
                    # With strict mode, this should never happen
                    # But we handle it gracefully just in case
                    extracted_data = None
                break

        # Calculate token usage
        usage = response.usage
        total_tokens = usage.input_tokens + usage.output_tokens

        # Log cache efficiency if caching is enabled
        if use_cache:
            cache_creation = getattr(usage, "cache_creation_input_tokens", 0)
            cache_read = getattr(usage, "cache_read_input_tokens", 0)
            logger.info(
                f"Extraction tokens: {total_tokens} total "
                f"(cached: {cache_read}, cache_creation: {cache_creation})"
            )

        return ExtractionResult(
            data=extracted_data,
            tokens_used=total_tokens,
            model_used=self.model
        )
```

**Key implementation details:**

1. **Strict mode:** `"strict": True` guarantees valid JSON (no parsing errors)
2. **Tool choice:** Forces Claude to use our extraction tool
3. **Prompt caching:** `cache_control` on system prompt reduces costs
4. **Validation:** Even with strict mode, we validate with Pydantic (defense in depth)
5. **Token logging:** Track usage for cost monitoring
6. **Error handling:** Clear error messages and logging

### Step 8: Implement Retry Logic

LLM APIs can fail (rate limits, transient errors). Professional applications implement retry logic with exponential backoff.

Add to `LLMService`:

```python
import asyncio
from anthropic import (
    AsyncAnthropic,
    APIError,
    APIConnectionError,
    RateLimitError,
    InternalServerError
)


class LLMService:
    # ... previous methods ...

    async def _call_claude_with_retry(
        self,
        system: list[dict],
        messages: list[dict],
        tools: list[ToolParam] | None = None,
        tool_choice: dict | None = None,
        max_retries: int = 3,
        initial_delay: float = 1.0
    ) -> Message:
        """
        Call Claude API with exponential backoff retry logic.

        Retries on:
        - Rate limit errors (429)
        - Internal server errors (500-599)
        - Connection errors

        Args:
            system: System prompt blocks
            messages: User/assistant messages
            tools: Tool definitions for structured output
            tool_choice: Force Claude to use specific tool
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds (doubles each retry)

        Returns:
            Claude API response message

        Raises:
            APIError: If all retries are exhausted
        """
        delay = initial_delay

        for attempt in range(max_retries + 1):
            try:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=system,
                    messages=messages,
                    tools=tools,
                    tool_choice=tool_choice
                )
                return response

            except (RateLimitError, InternalServerError, APIConnectionError) as e:
                # These errors are retryable
                if attempt == max_retries:
                    logger.error(
                        f"Claude API call failed after {max_retries} retries: {e}"
                    )
                    raise

                logger.warning(
                    f"Claude API error (attempt {attempt + 1}/{max_retries}): {e}. "
                    f"Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff

            except APIError as e:
                # Other API errors (invalid request, etc.) are not retryable
                logger.error(f"Non-retryable Claude API error: {e}")
                raise
```

**Why retry logic matters:**

1. **Rate limits (429):** APIs have limits; retry after delay
2. **Transient errors (500):** Server issues; retry succeeds
3. **Network issues:** Connection drops; retry reconnects
4. **Exponential backoff:** Prevents thundering herd (1s → 2s → 4s delays)

**What NOT to retry:**

- **400 Bad Request:** Invalid input (fix code, don't retry)
- **401 Unauthorized:** Invalid API key (retry won't help)
- **404 Not Found:** Wrong endpoint (retry won't help)

### Step 9: Add the System Prompt Constant

Add the system prompt constant at the top of `llm_service.py` (after imports):

```python
# System prompt for model extraction
# This is cached when use_cache=True to reduce costs
SYSTEM_PROMPT = """You are a data extraction assistant for an AI Model Catalogue database.

Your task is to extract information about AI models from unstructured text sources like:
- Research papers
- Technical blog posts
- News articles
- Benchmark reports

Extract the following fields:
- model_name: The technical identifier (e.g., "gpt-4", "claude-3-sonnet")
- display_name: Human-readable name (e.g., "GPT-4", "Claude 3 Sonnet")
- organization: The company/institution that created it
- release_date: When it was released (ISO format YYYY-MM-DD)
- description: Brief description of the model's purpose/capabilities
- license: License type if mentioned (e.g., "Apache 2.0", "Proprietary")
- metadata_: Additional structured information (context_window, pricing, etc.)

Important guidelines:
- Only extract information explicitly stated in the text
- Use null for missing fields rather than guessing
- Normalize model names to lowercase with hyphens (gpt-4, not GPT4)
- Infer release_date from context clues ("in March 2023" → "2023-03-01")
- Keep descriptions concise (1-2 sentences)
- Extract metadata as a JSON object when additional details are mentioned

Examples:

<example>
Input: "OpenAI released GPT-4 in March 2023. GPT-4 is a large multimodal model capable of processing both text and images."
Output:
{
  "model_name": "gpt-4",
  "display_name": "GPT-4",
  "organization": "OpenAI",
  "release_date": "2023-03-01",
  "description": "A large multimodal model capable of processing both text and images",
  "license": null,
  "metadata_": null
}
</example>

<example>
Input: "Anthropic's Claude 3.5 Sonnet, released June 2024, is licensed under a proprietary license."
Output:
{
  "model_name": "claude-3.5-sonnet",
  "display_name": "Claude 3.5 Sonnet",
  "organization": "Anthropic",
  "release_date": "2024-06-01",
  "description": null,
  "license": "Proprietary",
  "metadata_": null
}
</example>

<example>
Input: "Meta's LLaMA 2 70B was open-sourced in July 2023 with a context window of 4096 tokens."
Output:
{
  "model_name": "llama-2-70b",
  "display_name": "LLaMA 2 70B",
  "organization": "Meta",
  "release_date": "2023-07-01",
  "description": "Open-source model",
  "license": "Open Source",
  "metadata_": {"context_window": 4096}
}
</example>

<example>
Input: "This model is amazing! Highly recommended."
Output: null
(No extractable model information - text is too vague)
</example>

<example>
Input: ""
Output: null
(Empty input)
</example>

Now extract model information from the text provided by the user. If no valid model information can be extracted, return null for all fields.
"""
```

---

## Complete LLM Service Implementation

Here's the complete `llm_service.py` file with all pieces together:

**File:** `backend/app/services/llm_service.py`

```python
"""
LLM Service for Claude API Integration

This service handles all interactions with Claude (Anthropic's LLM),
including data extraction, prompt engineering, and response validation.
"""

import asyncio
import logging
from datetime import date
from typing import Any

from anthropic import (
    AsyncAnthropic,
    APIError,
    APIConnectionError,
    RateLimitError,
    InternalServerError
)
from anthropic.types import Message, ToolParam
from pydantic import BaseModel, Field, ValidationError

from app.config import settings

logger = logging.getLogger(__name__)


# System prompt for model extraction
# This is cached when use_cache=True to reduce costs
SYSTEM_PROMPT = """You are a data extraction assistant for an AI Model Catalogue database.

Your task is to extract information about AI models from unstructured text sources like:
- Research papers
- Technical blog posts
- News articles
- Benchmark reports

Extract the following fields:
- model_name: The technical identifier (e.g., "gpt-4", "claude-3-sonnet")
- display_name: Human-readable name (e.g., "GPT-4", "Claude 3 Sonnet")
- organization: The company/institution that created it
- release_date: When it was released (ISO format YYYY-MM-DD)
- description: Brief description of the model's purpose/capabilities
- license: License type if mentioned (e.g., "Apache 2.0", "Proprietary")
- metadata_: Additional structured information (context_window, pricing, etc.)

Important guidelines:
- Only extract information explicitly stated in the text
- Use null for missing fields rather than guessing
- Normalize model names to lowercase with hyphens (gpt-4, not GPT4)
- Infer release_date from context clues ("in March 2023" → "2023-03-01")
- Keep descriptions concise (1-2 sentences)
- Extract metadata as a JSON object when additional details are mentioned

Examples:

<example>
Input: "OpenAI released GPT-4 in March 2023. GPT-4 is a large multimodal model capable of processing both text and images."
Output:
{
  "model_name": "gpt-4",
  "display_name": "GPT-4",
  "organization": "OpenAI",
  "release_date": "2023-03-01",
  "description": "A large multimodal model capable of processing both text and images",
  "license": null,
  "metadata_": null
}
</example>

<example>
Input: "Anthropic's Claude 3.5 Sonnet, released June 2024, is licensed under a proprietary license."
Output:
{
  "model_name": "claude-3.5-sonnet",
  "display_name": "Claude 3.5 Sonnet",
  "organization": "Anthropic",
  "release_date": "2024-06-01",
  "description": null,
  "license": "Proprietary",
  "metadata_": null
}
</example>

<example>
Input: "Meta's LLaMA 2 70B was open-sourced in July 2023 with a context window of 4096 tokens."
Output:
{
  "model_name": "llama-2-70b",
  "display_name": "LLaMA 2 70B",
  "organization": "Meta",
  "release_date": "2023-07-01",
  "description": "Open-source model",
  "license": "Open Source",
  "metadata_": {"context_window": 4096}
}
</example>

<example>
Input: "This model is amazing! Highly recommended."
Output: null
(No extractable model information - text is too vague)
</example>

<example>
Input: ""
Output: null
(Empty input)
</example>

Now extract model information from the text provided by the user. If no valid model information can be extracted, return null for all fields.
"""


class ExtractedModel(BaseModel):
    """
    Schema for AI model data extracted by LLM.

    Matches ModelCreate but all fields are optional since
    extraction may not find complete information.
    """
    model_name: str | None = Field(
        None,
        description="Technical model identifier (lowercase with hyphens)",
        examples=["gpt-4", "claude-3-sonnet", "llama-2"]
    )
    display_name: str | None = Field(
        None,
        description="Human-readable model name",
        examples=["GPT-4", "Claude 3 Sonnet", "LLaMA 2"]
    )
    organization: str | None = Field(
        None,
        description="Organization that created the model",
        examples=["OpenAI", "Anthropic", "Meta"]
    )
    release_date: date | None = Field(
        None,
        description="Release date in ISO format (YYYY-MM-DD)"
    )
    description: str | None = Field(
        None,
        description="Brief description of model capabilities"
    )
    license: str | None = Field(
        None,
        description="License type",
        examples=["Apache 2.0", "MIT", "Proprietary", "Open Source"]
    )
    metadata_: dict | None = Field(
        None,
        description="Additional metadata (context window, pricing, etc.)"
    )


class ExtractionResult(BaseModel):
    """
    Result of an LLM extraction operation.

    Contains the extracted data plus metadata about the extraction
    (tokens used, model, extraction confidence, etc.)
    """
    data: ExtractedModel | None = Field(
        None,
        description="Extracted model data, or None if no data could be extracted"
    )
    tokens_used: int = Field(
        description="Total tokens used in the extraction"
    )
    model_used: str = Field(
        description="Claude model used for extraction"
    )


class LLMService:
    """
    Service for interacting with Claude API.

    Handles prompt engineering, structured extraction, caching,
    and error handling for LLM-powered features.
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize the LLM service with Claude API client.

        Args:
            api_key: Anthropic API key. If None, uses settings.anthropic_api_key
        """
        self.api_key = api_key or settings.anthropic_api_key
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not configured. Set ANTHROPIC_API_KEY in .env"
            )

        # Initialize async client
        self.client = AsyncAnthropic(api_key=self.api_key)

        # Default model - Sonnet 4.5 for complex extraction
        self.model = "claude-sonnet-4-5-20250929"

    async def close(self):
        """Close the API client. Call this in cleanup/shutdown."""
        await self.client.close()

    async def extract_model_data(
        self,
        text: str,
        use_cache: bool = True
    ) -> ExtractionResult:
        """
        Extract AI model information from unstructured text.

        Uses Claude with structured outputs (strict mode) to guarantee
        valid JSON responses matching the ExtractedModel schema.

        Args:
            text: The text to extract model information from
            use_cache: Enable prompt caching to reduce costs (default: True)

        Returns:
            ExtractionResult with extracted data and token usage

        Raises:
            ValueError: If text is empty
            anthropic.APIError: If the API call fails after retries
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Define the extraction tool with strict schema
        extract_tool: ToolParam = {
            "name": "extract_model",
            "description": "Extract AI model information from text",
            "input_schema": {
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": ["string", "null"],
                        "description": "Technical model identifier (lowercase with hyphens)"
                    },
                    "display_name": {
                        "type": ["string", "null"],
                        "description": "Human-readable model name"
                    },
                    "organization": {
                        "type": ["string", "null"],
                        "description": "Organization that created the model"
                    },
                    "release_date": {
                        "type": ["string", "null"],
                        "description": "Release date in ISO format (YYYY-MM-DD)",
                        "format": "date"
                    },
                    "description": {
                        "type": ["string", "null"],
                        "description": "Brief description of model capabilities"
                    },
                    "license": {
                        "type": ["string", "null"],
                        "description": "License type"
                    },
                    "metadata_": {
                        "type": ["object", "null"],
                        "description": "Additional metadata"
                    }
                },
                "required": []  # All fields optional
            },
            "strict": True  # ✨ Strict mode guarantees schema conformance
        }

        # Build system prompt with caching
        system_blocks = [
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
            }
        ]
        # Add cache control only if use_cache is True
        if use_cache:
            system_blocks[0]["cache_control"] = {"type": "ephemeral"}

        # Call Claude with retry logic
        try:
            response = await self._call_claude_with_retry(
                system=system_blocks,
                messages=[
                    {
                        "role": "user",
                        "content": f"Extract model information from this text:\n\n{text}"
                    }
                ],
                tools=[extract_tool],
                tool_choice={"type": "tool", "name": "extract_model"}
            )
        except Exception as e:
            logger.error(f"Failed to extract model data: {e}")
            raise

        # Extract the tool use from response
        extracted_data = None
        for content_block in response.content:
            if content_block.type == "tool_use" and content_block.name == "extract_model":
                # Claude returns the data in content_block.input
                raw_data = content_block.input

                # Validate against our Pydantic schema
                try:
                    extracted_data = ExtractedModel(**raw_data)
                except ValidationError as e:
                    logger.error(f"Extracted data failed validation: {e}")
                    # With strict mode, this should never happen
                    # But we handle it gracefully just in case
                    extracted_data = None
                break

        # Calculate token usage
        usage = response.usage
        total_tokens = usage.input_tokens + usage.output_tokens

        # Log cache efficiency if caching is enabled
        if use_cache:
            cache_creation = getattr(usage, "cache_creation_input_tokens", 0)
            cache_read = getattr(usage, "cache_read_input_tokens", 0)
            logger.info(
                f"Extraction tokens: {total_tokens} total "
                f"(cached: {cache_read}, cache_creation: {cache_creation})"
            )

        return ExtractionResult(
            data=extracted_data,
            tokens_used=total_tokens,
            model_used=self.model
        )

    async def _call_claude_with_retry(
        self,
        system: list[dict],
        messages: list[dict],
        tools: list[ToolParam] | None = None,
        tool_choice: dict | None = None,
        max_retries: int = 3,
        initial_delay: float = 1.0
    ) -> Message:
        """
        Call Claude API with exponential backoff retry logic.

        Retries on:
        - Rate limit errors (429)
        - Internal server errors (500-599)
        - Connection errors

        Args:
            system: System prompt blocks
            messages: User/assistant messages
            tools: Tool definitions for structured output
            tool_choice: Force Claude to use specific tool
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds (doubles each retry)

        Returns:
            Claude API response message

        Raises:
            APIError: If all retries are exhausted
        """
        delay = initial_delay

        for attempt in range(max_retries + 1):
            try:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=system,
                    messages=messages,
                    tools=tools,
                    tool_choice=tool_choice
                )
                return response

            except (RateLimitError, InternalServerError, APIConnectionError) as e:
                # These errors are retryable
                if attempt == max_retries:
                    logger.error(
                        f"Claude API call failed after {max_retries} retries: {e}"
                    )
                    raise

                logger.warning(
                    f"Claude API error (attempt {attempt + 1}/{max_retries}): {e}. "
                    f"Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff

            except APIError as e:
                # Other API errors (invalid request, etc.) are not retryable
                logger.error(f"Non-retryable Claude API error: {e}")
                raise
```

---

## Testing the LLM Service

Testing LLM integrations is tricky. You don't want to call the real API in every test (expensive, slow, non-deterministic). The solution: **mock the API responses**.

### Step 1: Create Test File

Create `backend/tests/test_llm_service.py`:

```python
"""
Tests for LLM Service

Tests extraction logic, error handling, and retry behavior
using mocked Claude API responses.
"""

import pytest
from datetime import date
from unittest.mock import AsyncMock, Mock, patch
from anthropic.types import (
    Message,
    Usage,
    ContentBlock,
    ToolUseBlock
)

from app.services.llm_service import (
    LLMService,
    ExtractedModel,
    ExtractionResult,
    SYSTEM_PROMPT
)


@pytest.fixture
def llm_service():
    """Create LLMService with test API key"""
    return LLMService(api_key="test-key-123")


@pytest.fixture
def mock_claude_response():
    """
    Mock Claude API response for successful extraction.

    Simulates the response structure from Claude's API
    including tool use and token usage.
    """
    def _create_response(extracted_data: dict) -> Message:
        """Create a mock Message with the given extracted data"""

        # Create tool use block
        tool_use = Mock(spec=ToolUseBlock)
        tool_use.type = "tool_use"
        tool_use.name = "extract_model"
        tool_use.input = extracted_data

        # Create usage stats
        usage = Mock(spec=Usage)
        usage.input_tokens = 500
        usage.output_tokens = 150
        usage.cache_creation_input_tokens = 0
        usage.cache_read_input_tokens = 0

        # Create message
        message = Mock(spec=Message)
        message.content = [tool_use]
        message.usage = usage

        return message

    return _create_response


class TestLLMServiceInitialization:
    """Test service initialization and configuration"""

    def test_init_with_api_key(self):
        """Service initializes with provided API key"""
        service = LLMService(api_key="test-key")
        assert service.api_key == "test-key"
        assert service.model == "claude-sonnet-4-5-20250929"

    def test_init_without_api_key_raises_error(self):
        """Service raises error if no API key configured"""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.anthropic_api_key = ""

            with pytest.raises(ValueError, match="API key not configured"):
                LLMService()

    async def test_close_client(self, llm_service):
        """Service closes API client properly"""
        llm_service.client.close = AsyncMock()
        await llm_service.close()
        llm_service.client.close.assert_called_once()


class TestModelExtraction:
    """Test model data extraction from text"""

    async def test_extract_complete_model_data(
        self, llm_service, mock_claude_response
    ):
        """Successfully extract complete model information"""

        # Mock API response with complete data
        extracted = {
            "model_name": "gpt-4",
            "display_name": "GPT-4",
            "organization": "OpenAI",
            "release_date": "2023-03-01",
            "description": "A large multimodal model",
            "license": "Proprietary",
            "metadata_": {"context_window": 8192}
        }

        with patch.object(
            llm_service, "_call_claude_with_retry",
            return_value=mock_claude_response(extracted)
        ):
            result = await llm_service.extract_model_data(
                "GPT-4 was released by OpenAI in March 2023..."
            )

        assert isinstance(result, ExtractionResult)
        assert result.data is not None
        assert result.data.model_name == "gpt-4"
        assert result.data.display_name == "GPT-4"
        assert result.data.organization == "OpenAI"
        assert result.data.release_date == date(2023, 3, 1)
        assert result.data.description == "A large multimodal model"
        assert result.data.license == "Proprietary"
        assert result.data.metadata_ == {"context_window": 8192}
        assert result.tokens_used == 650  # 500 + 150
        assert result.model_used == "claude-sonnet-4-5-20250929"

    async def test_extract_partial_model_data(
        self, llm_service, mock_claude_response
    ):
        """Extract model with only some fields available"""

        # Mock API response with partial data
        extracted = {
            "model_name": "claude-3-sonnet",
            "display_name": "Claude 3 Sonnet",
            "organization": "Anthropic",
            "release_date": None,
            "description": None,
            "license": None,
            "metadata_": None
        }

        with patch.object(
            llm_service, "_call_claude_with_retry",
            return_value=mock_claude_response(extracted)
        ):
            result = await llm_service.extract_model_data(
                "Claude 3 Sonnet by Anthropic"
            )

        assert result.data is not None
        assert result.data.model_name == "claude-3-sonnet"
        assert result.data.organization == "Anthropic"
        assert result.data.release_date is None
        assert result.data.description is None

    async def test_extract_no_data_found(
        self, llm_service, mock_claude_response
    ):
        """Handle text with no extractable model information"""

        # Mock API response with all null values
        extracted = {
            "model_name": None,
            "display_name": None,
            "organization": None,
            "release_date": None,
            "description": None,
            "license": None,
            "metadata_": None
        }

        with patch.object(
            llm_service, "_call_claude_with_retry",
            return_value=mock_claude_response(extracted)
        ):
            result = await llm_service.extract_model_data(
                "This is a random sentence with no model info."
            )

        # Service returns result but all fields are None
        assert result.data is not None
        assert result.data.model_name is None
        assert result.data.organization is None

    async def test_extract_empty_text_raises_error(self, llm_service):
        """Empty text raises ValueError"""

        with pytest.raises(ValueError, match="Text cannot be empty"):
            await llm_service.extract_model_data("")

        with pytest.raises(ValueError, match="Text cannot be empty"):
            await llm_service.extract_model_data("   ")

    async def test_extract_with_cache_enabled(
        self, llm_service, mock_claude_response
    ):
        """Extraction uses prompt caching when enabled"""

        extracted = {"model_name": "gpt-4", "display_name": "GPT-4"}

        # Mock the response with cache stats
        response = mock_claude_response(extracted)
        response.usage.cache_creation_input_tokens = 450  # First call creates cache
        response.usage.cache_read_input_tokens = 0

        with patch.object(
            llm_service, "_call_claude_with_retry", return_value=response
        ) as mock_call:
            await llm_service.extract_model_data("GPT-4", use_cache=True)

            # Verify cache_control was added to system prompt
            call_args = mock_call.call_args
            system_blocks = call_args.kwargs["system"]
            assert system_blocks[0]["cache_control"] == {"type": "ephemeral"}

    async def test_extract_without_cache(
        self, llm_service, mock_claude_response
    ):
        """Extraction works without caching"""

        extracted = {"model_name": "gpt-4"}

        with patch.object(
            llm_service, "_call_claude_with_retry",
            return_value=mock_claude_response(extracted)
        ) as mock_call:
            await llm_service.extract_model_data("GPT-4", use_cache=False)

            # Verify cache_control was NOT added
            call_args = mock_call.call_args
            system_blocks = call_args.kwargs["system"]
            assert "cache_control" not in system_blocks[0]


class TestRetryLogic:
    """Test API retry behavior with exponential backoff"""

    async def test_successful_call_no_retry(self, llm_service):
        """Successful API call doesn't trigger retry"""

        mock_response = Mock()
        llm_service.client.messages.create = AsyncMock(return_value=mock_response)

        result = await llm_service._call_claude_with_retry(
            system=[{"type": "text", "text": "test"}],
            messages=[{"role": "user", "content": "test"}]
        )

        assert result == mock_response
        assert llm_service.client.messages.create.call_count == 1

    async def test_rate_limit_retry_success(self, llm_service):
        """Rate limit error triggers retry and succeeds"""
        from anthropic import RateLimitError

        mock_response = Mock()

        # First call raises RateLimitError, second succeeds
        llm_service.client.messages.create = AsyncMock(
            side_effect=[
                RateLimitError("Rate limit exceeded", response=Mock(), body=None),
                mock_response
            ]
        )

        result = await llm_service._call_claude_with_retry(
            system=[{"type": "text", "text": "test"}],
            messages=[{"role": "user", "content": "test"}],
            initial_delay=0.01  # Fast retry for tests
        )

        assert result == mock_response
        assert llm_service.client.messages.create.call_count == 2

    async def test_max_retries_exceeded(self, llm_service):
        """Exhausting all retries raises the error"""
        from anthropic import RateLimitError

        # All calls raise RateLimitError
        error = RateLimitError("Rate limit exceeded", response=Mock(), body=None)
        llm_service.client.messages.create = AsyncMock(side_effect=error)

        with pytest.raises(RateLimitError):
            await llm_service._call_claude_with_retry(
                system=[{"type": "text", "text": "test"}],
                messages=[{"role": "user", "content": "test"}],
                max_retries=2,
                initial_delay=0.01
            )

        # Called 3 times: initial + 2 retries
        assert llm_service.client.messages.create.call_count == 3

    async def test_non_retryable_error_no_retry(self, llm_service):
        """Non-retryable errors (400, 401) don't trigger retry"""
        from anthropic import BadRequestError

        error = BadRequestError("Invalid request", response=Mock(), body=None)
        llm_service.client.messages.create = AsyncMock(side_effect=error)

        with pytest.raises(BadRequestError):
            await llm_service._call_claude_with_retry(
                system=[{"type": "text", "text": "test"}],
                messages=[{"role": "user", "content": "test"}]
            )

        # Only called once - no retry
        assert llm_service.client.messages.create.call_count == 1

    async def test_exponential_backoff_timing(self, llm_service):
        """Retry delays follow exponential backoff pattern"""
        from anthropic import InternalServerError
        import time

        error = InternalServerError("Server error", response=Mock(), body=None)
        llm_service.client.messages.create = AsyncMock(side_effect=error)

        start = time.time()

        with pytest.raises(InternalServerError):
            await llm_service._call_claude_with_retry(
                system=[{"type": "text", "text": "test"}],
                messages=[{"role": "user", "content": "test"}],
                max_retries=2,
                initial_delay=0.1
            )

        elapsed = time.time() - start

        # Should wait: 0.1s + 0.2s + 0.4s = 0.7s total
        # Allow some tolerance for execution time
        assert elapsed >= 0.6
```

**Testing strategies:**

1. **Mock API responses:** Use `unittest.mock` to simulate Claude responses
2. **Test edge cases:** Empty text, partial data, no data
3. **Test error handling:** Rate limits, retries, non-retryable errors
4. **Test caching:** Verify cache_control is added correctly
5. **Fast tests:** Use short delays for retry tests

### Step 2: Run Tests

```bash
cd backend
uv run pytest tests/test_llm_service.py -v
```

Expected output:

```
tests/test_llm_service.py::TestLLMServiceInitialization::test_init_with_api_key PASSED
tests/test_llm_service.py::TestLLMServiceInitialization::test_init_without_api_key_raises_error PASSED
tests/test_llm_service.py::TestModelExtraction::test_extract_complete_model_data PASSED
tests/test_llm_service.py::TestModelExtraction::test_extract_partial_model_data PASSED
...
==================== 14 passed in 0.42s ====================
```

---

## Manual Testing with Real API

Now let's test with the **real Claude API** to verify everything works. We'll mark this as a slow test so it doesn't run by default.

Add to `test_llm_service.py`:

```python
@pytest.mark.slow
class TestRealAPIIntegration:
    """
    Integration tests with real Claude API.

    Run with: pytest -m slow
    These tests cost ~$0.01 per run.
    """

    @pytest.fixture
    def real_llm_service(self):
        """Create LLMService with real API key from settings"""
        from app.config import settings

        if not settings.anthropic_api_key:
            pytest.skip("ANTHROPIC_API_KEY not configured")

        return LLMService()

    async def test_extract_gpt4_announcement(self, real_llm_service):
        """Extract data from GPT-4 announcement text"""

        text = """
        OpenAI announced GPT-4 on March 14, 2023. GPT-4 is a large multimodal
        model that can accept image and text inputs and produce text outputs.
        It exhibits human-level performance on various professional and academic
        benchmarks. GPT-4 is available via API with a proprietary license.
        """

        result = await real_llm_service.extract_model_data(text)

        # Verify extraction
        assert result.data is not None
        assert result.data.model_name == "gpt-4"
        assert result.data.organization == "OpenAI"
        assert result.data.release_date == date(2023, 3, 14)
        assert "multimodal" in result.data.description.lower()
        assert result.data.license == "Proprietary"

        # Verify token usage is reasonable
        assert result.tokens_used > 0
        assert result.tokens_used < 5000  # Should be much less

        print(f"\n✅ Successfully extracted: {result.data}")
        print(f"📊 Tokens used: {result.tokens_used}")

    async def test_extract_with_prompt_caching(self, real_llm_service):
        """Test that prompt caching reduces tokens on second call"""

        text1 = "Claude 3 Opus was released by Anthropic in March 2024."
        text2 = "Claude 3 Sonnet was released by Anthropic in March 2024."

        # First call - creates cache
        result1 = await real_llm_service.extract_model_data(text1, use_cache=True)
        tokens_first = result1.tokens_used

        # Second call - should use cache (fewer input tokens)
        result2 = await real_llm_service.extract_model_data(text2, use_cache=True)
        tokens_second = result2.tokens_used

        print(f"\n📊 First call tokens: {tokens_first}")
        print(f"📊 Second call tokens: {tokens_second}")
        print(f"💰 Savings: {tokens_first - tokens_second} tokens")

        # Both should extract successfully
        assert result1.data.model_name == "claude-3-opus"
        assert result2.data.model_name == "claude-3-sonnet"
```

Run the slow tests:

```bash
# Run only slow tests (real API calls)
uv run pytest tests/test_llm_service.py -m slow -v -s

# Expected output:
# ✅ Successfully extracted: model_name='gpt-4' organization='OpenAI'...
# 📊 Tokens used: 1847
# 📊 First call tokens: 1923
# 📊 Second call tokens: 674
# 💰 Savings: 1249 tokens
```

**Understanding the output:**

- **First call:** Creates the cache (~1900 tokens)
- **Second call:** Uses cached system prompt (~670 tokens)
- **Savings:** ~65% fewer tokens on subsequent calls!

This demonstrates why prompt caching is valuable during development.

---

## Hands-On Exercises

### Exercise 1: Add Benchmark Extraction

**Objective:** Extend the LLM service to extract benchmark information from text.

**Instructions:**

1. Create an `ExtractedBenchmark` schema matching the `BenchmarkCreate` model
2. Add a `BENCHMARK_SYSTEM_PROMPT` with extraction guidelines
3. Implement `extract_benchmark_data(text: str)` method in `LLMService`
4. Write tests for benchmark extraction (mock and real)

**Acceptance Criteria:**

- Extracts benchmark name, category, description, URL
- Handles missing fields gracefully
- Uses structured outputs with `strict: true`
- Has test coverage >80%

**Example input:**

```
"MMLU (Massive Multitask Language Understanding) is a reasoning benchmark that
tests models across 57 subjects. Learn more at https://arxiv.org/abs/2009.03300"
```

**Expected output:**

```python
{
  "name": "MMLU",
  "category": "Reasoning",
  "description": "Tests models across 57 subjects",
  "url": "https://arxiv.org/abs/2009.03300"
}
```

<details>
<summary>Example Solution</summary>

```python
# In llm_service.py

BENCHMARK_SYSTEM_PROMPT = """You are a data extraction assistant for an AI Model Catalogue database.

Extract benchmark information from text with these fields:
- name: Benchmark name/acronym (e.g., "MMLU", "HumanEval")
- category: Type of benchmark (e.g., "Reasoning", "Coding", "Math")
- description: What the benchmark tests
- url: Link to benchmark details/paper

Examples:

<example>
Input: "MMLU tests language understanding across 57 subjects."
Output: {
  "name": "MMLU",
  "category": "Reasoning",
  "description": "Tests language understanding across 57 subjects",
  "url": null
}
</example>

Extract benchmark information from the user's text.
"""

class ExtractedBenchmark(BaseModel):
    name: str | None = None
    category: str | None = None
    description: str | None = None
    url: str | None = None

async def extract_benchmark_data(self, text: str) -> ExtractionResult:
    # Similar to extract_model_data but with benchmark schema
    pass
```

</details>

### Exercise 2: Batch Extraction

**Objective:** Extract multiple models from a single text input.

**Instructions:**

1. Create `extract_multiple_models(text: str)` that returns a list of `ExtractedModel`
2. Update the tool schema to support array responses
3. Test with text mentioning multiple models

**Example:**

```
"The evaluation compared GPT-4 by OpenAI, Claude 3 Opus by Anthropic,
and Gemini Pro by Google across multiple benchmarks."
```

Should extract all three models.

### Exercise 3: Model Selection

**Objective:** Allow callers to choose between Haiku and Sonnet models.

**Instructions:**

1. Add `model: str` parameter to `extract_model_data`
2. Support "haiku" and "sonnet" as aliases
3. Compare extraction quality and cost between models
4. Document when to use each model

**Test:**

```python
# Fast, cheap extraction with Haiku
result_haiku = await service.extract_model_data(text, model="haiku")

# High-quality extraction with Sonnet
result_sonnet = await service.extract_model_data(text, model="sonnet")

print(f"Haiku tokens: {result_haiku.tokens_used}")
print(f"Sonnet tokens: {result_sonnet.tokens_used}")
```

### Exercise 4: Extended Thinking for Complex Text

**Objective:** Use Claude's extended thinking for complex extraction scenarios.

**Instructions:**

1. Add `use_extended_thinking: bool` parameter to extraction methods
2. Enable extended thinking for ambiguous or complex text
3. Compare results with and without extended thinking

**When to use:**

- Long research papers with complex language
- Ambiguous model names (is "GPT-4 Turbo" a separate model?)
- Conflicting information in text

---

## Common Pitfalls

### Pitfall 1: Not Validating Extracted Data

**Symptom:** Extracted data has invalid values (dates in wrong format, empty strings instead of None)

**Solution:**

Always validate extracted data against Pydantic schemas before database insertion:

```python
# ❌ Don't trust LLM output blindly
await repo.create(Model(**extracted_data))

# ✅ Validate first
try:
    validated = ExtractedModel(**extracted_data)
    if validated.model_name:  # Check required fields
        await repo.create(Model(**validated.model_dump()))
except ValidationError as e:
    logger.error(f"Invalid extracted data: {e}")
```

### Pitfall 2: Ignoring Token Costs

**Symptom:** API bills are higher than expected

**Solution:**

1. **Use prompt caching:** Reduces costs by 90% on repeated calls
2. **Choose the right model:** Haiku for simple tasks, Sonnet for complex
3. **Log token usage:** Monitor and set alerts
4. **Limit max_tokens:** Don't generate more than needed

```python
# Monitor token usage
logger.info(f"Extraction used {result.tokens_used} tokens")

# Alert if usage is unusually high
if result.tokens_used > 10000:
    logger.warning("High token usage detected!")
```

### Pitfall 3: Hardcoding Prompts in Code

**Symptom:** Changing prompts requires code changes and redeployment

**Solution:**

Store prompts in configuration or database:

```python
# ❌ Hardcoded
PROMPT = "Extract model info from text"

# ✅ Configurable
class PromptConfig(BaseModel):
    model_extraction: str = Field(default=DEFAULT_MODEL_PROMPT)

# Load from config file or database
prompts = PromptConfig.parse_file("prompts.json")
```

### Pitfall 4: Not Handling Rate Limits

**Symptom:** `RateLimitError` crashes your application

**Solution:**

Our retry logic handles this, but for production:

1. **Implement rate limiting:** Don't exceed API limits
2. **Use exponential backoff:** Our `_call_claude_with_retry` does this
3. **Queue requests:** For batch processing, use a job queue

### Pitfall 5: Testing with Real API in CI/CD

**Symptom:** Tests are slow, expensive, and fail due to API issues

**Solution:**

- **Default tests use mocks:** Fast, free, deterministic
- **Slow tests marked with `@pytest.mark.slow`:** Run manually
- **CI/CD runs only mocked tests:** Fast pipeline

```bash
# Fast tests (mocked, in CI/CD)
pytest

# Slow tests (real API, manual)
pytest -m slow
```

---

## Key Takeaways

1. **Service Layer Pattern:** Separates business logic (LLM extraction) from HTTP handling (API endpoints)
2. **Structured Outputs:** Use `strict: true` for guaranteed schema conformance
3. **Prompt Engineering:** Be explicit, provide context, use 3-5 examples, positive framing
4. **Prompt Caching:** Reduces costs by 90% on repeated calls (requires 1024+ tokens)
5. **Error Handling:** Retry rate limits and transient errors with exponential backoff
6. **Validation:** Always validate LLM outputs against schemas before database insertion
7. **Testing:** Mock API responses for fast, cheap, deterministic tests
8. **Model Selection:** Sonnet for complex extraction, Haiku for simple tasks
9. **Token Monitoring:** Log usage to track costs and optimize prompts

---

## Further Reading

### Anthropic Documentation

- **Prompt Engineering Guide:** https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
- **Claude 4.5 Best Practices:** https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices
- **Structured Outputs (Tool Use):** https://docs.anthropic.com/en/docs/build-with-claude/tool-use
- **Prompt Caching:** https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
- **API Reference:** https://docs.anthropic.com/en/api/messages

### Related Concepts

- **FastAPI Dependency Injection:** https://fastapi.tiangolo.com/tutorial/dependencies/
- **Pydantic Validation:** https://docs.pydantic.dev/latest/concepts/validators/
- **Async Python:** https://realpython.com/async-io-python/
- **Testing with Mocks:** https://docs.python.org/3/library/unittest.mock.html

### Industry Resources

- **Prompt Engineering Best Practices:** https://platform.openai.com/docs/guides/prompt-engineering
- **LLM Security:** https://owasp.org/www-project-top-10-for-large-language-model-applications/
- **Cost Optimization:** https://www.anthropic.com/pricing

---

## Next Steps

Congratulations! You've built a production-ready LLM service with Claude integration. You can now extract structured data from arbitrary text using AI.

**In Module 3.2 (Manual Input Endpoint)**, you'll:

1. Create a `/api/v1/extract` POST endpoint that accepts text
2. Use your `LLMService` to extract model data
3. Validate extracted data and insert into the database
4. Handle duplicate models and validation errors
5. Return the created model with proper HTTP status codes

**Preview of Module 3.2:**

```python
@router.post("/extract", response_model=ModelResponse, status_code=201)
async def extract_and_create_model(
    request: ExtractRequest,
    llm_service: LLMService = Depends(get_llm_service),
    session: AsyncSession = Depends(get_db)
):
    """
    Extract model information from text and create database entry.

    Uses Claude API to parse unstructured text and automatically
    populate the model catalogue.
    """
    # Extract with LLM
    result = await llm_service.extract_model_data(request.text)

    # Validate and create model
    # ... (you'll implement this)
```

This connects your LLM service to your API endpoints, completing the manual extraction pipeline!

**Optional Challenge:** Before starting Module 3.2, try implementing the `/extract` endpoint yourself using what you've learned. Compare your solution with the module when ready.
