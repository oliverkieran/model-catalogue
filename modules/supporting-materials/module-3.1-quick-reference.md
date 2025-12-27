# Module 3.1: Quick Reference Guide

## LLM Service Cheat Sheet

### Basic Usage

```python
from app.services.llm_service import LLMService

# Initialize service (uses ANTHROPIC_API_KEY from .env)
llm_service = LLMService()

# Extract model data from text
result = await llm_service.extract_model_data(
    text="GPT-4 was released by OpenAI in March 2023",
    use_cache=True  # Enable prompt caching
)

# Access extracted data
if result.data:
    print(f"Model: {result.data.model_name}")
    print(f"Organization: {result.data.organization}")
    print(f"Tokens used: {result.tokens_used}")

# Clean up when done
await llm_service.close()
```

### Available Models

```python
# Sonnet 4.5 - Best for complex extraction (default)
llm_service.model = "claude-sonnet-4-5-20250929"

# Haiku 4.5 - Faster, cheaper for simple tasks
llm_service.model = "claude-haiku-4-5-20250929"

# Opus 4.5 - Most capable for very complex reasoning
llm_service.model = "claude-opus-4-5-20250929"
```

### Prompt Engineering Best Practices

1. **Be explicit:** "Extract these 5 fields: name, organization..."
2. **Provide context:** "This is for a model catalogue database..."
3. **Give 3-5 examples:** Cover normal, edge, and invalid cases
4. **Use structured formats:** XML tags, JSON schemas
5. **Positive framing:** "Do X" not "Don't do Y"
6. **Use strict mode:** `"strict": True` guarantees schema conformance

### Cost Optimization

```python
# Enable prompt caching (saves ~90% on repeated calls)
result = await llm_service.extract_model_data(text, use_cache=True)

# Choose appropriate model
# Simple extraction: Haiku (~$0.25 per million input tokens)
# Complex extraction: Sonnet (~$3 per million input tokens)

# Monitor token usage
print(f"Tokens used: {result.tokens_used}")
```

### Error Handling

The service automatically retries on:
- Rate limit errors (429)
- Internal server errors (500-599)
- Connection errors

With exponential backoff: 1s → 2s → 4s

```python
try:
    result = await llm_service.extract_model_data(text)
except ValueError as e:
    print(f"Invalid input: {e}")
except APIError as e:
    print(f"API error after retries: {e}")
```

### Testing

```python
# Mock API responses in tests
from unittest.mock import Mock, patch

mock_response = Mock()
mock_response.content = [
    Mock(type="tool_use", name="extract_model", input={"model_name": "gpt-4"})
]
mock_response.usage = Mock(input_tokens=500, output_tokens=150)

with patch.object(llm_service, "_call_claude_with_retry", return_value=mock_response):
    result = await llm_service.extract_model_data("test")
    assert result.data.model_name == "gpt-4"
```

### Common Patterns

**Extract and validate:**

```python
result = await llm_service.extract_model_data(text)

if result.data and result.data.model_name:
    # Convert to database schema
    model_create = ModelCreate(
        name=result.data.model_name,
        display_name=result.data.display_name,
        organization=result.data.organization,
        release_date=result.data.release_date,
        description=result.data.description,
        license=result.data.license,
        metadata_=result.data.metadata_
    )

    # Insert into database
    await model_repo.create(Model(**model_create.model_dump()))
else:
    print("No valid model data extracted")
```

**Batch processing with caching:**

```python
texts = [...]  # List of texts to process

for i, text in enumerate(texts):
    result = await llm_service.extract_model_data(
        text,
        use_cache=True  # First call creates cache, rest use it
    )
    print(f"Processed {i+1}/{len(texts)}, tokens: {result.tokens_used}")
```

### File Locations

- **Service implementation:** `backend/app/services/llm_service.py`
- **Tests:** `backend/tests/test_llm_service.py`
- **Configuration:** `backend/app/config.py` (ANTHROPIC_API_KEY)
- **Environment:** `backend/.env`

### Run Tests

```bash
# Fast tests (mocked, no API calls)
uv run pytest tests/test_llm_service.py -v

# Slow tests (real API, ~$0.01 cost)
uv run pytest tests/test_llm_service.py -m slow -v -s

# All tests
uv run pytest
```

### Troubleshooting

**"API key not configured"**
- Add `ANTHROPIC_API_KEY=sk-ant-...` to `backend/.env`
- Get key from https://console.anthropic.com

**"Rate limit exceeded"**
- Service automatically retries with backoff
- If persistent, reduce request rate or upgrade API plan

**High token usage**
- Enable prompt caching: `use_cache=True`
- Use Haiku model for simple tasks
- Reduce max_tokens in `_call_claude_with_retry`

**Extraction quality issues**
- Improve prompt with more examples
- Use Sonnet instead of Haiku for complex text
- Add extended thinking for ambiguous cases

### Next Steps

After mastering Module 3.1, proceed to:

**Module 3.2: Manual Input Endpoint**
- Create `/api/v1/extract` POST endpoint
- Integrate LLMService with CRUD operations
- Handle duplicate models and validation
- Return proper HTTP responses
