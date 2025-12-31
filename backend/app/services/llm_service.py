"""
LLM Service for Claude API Integration

This service handles all interactions with Claude,
including data extraction, prompt engineering, and response validation.
"""

import asyncio
import logging
from anthropic import (
    AsyncAnthropic,
    APIError,
    APIConnectionError,
    RateLimitError,
    InternalServerError,
)
from pydantic import BaseModel, Field
from datetime import date
from typing import Type

from app.config import settings

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-sonnet-4-5"

# System prompt for model extraction
# This is cached when use_cache=True to reduce costs
SYSTEM_PROMPT = """You are a data extraction assistant for an AI Model Catalogue database.

Your task is to extract information about AI models from unstructured text sources like:
- Research papers
- Technical blog posts
- News articles
- Benchmark reports

Important guidelines:
- Only extract information explicitly stated in the text
- Use null for missing fields rather than guessing
- Normalize model names to lowercase with hyphens (gpt-4, not GPT4)
- Infer release_date from context clues ("in March 2023" → "2023-03-01")
- Keep descriptions concise (1-2 sentences)
- Extract metadata as a JSON object when additional details are mentioned

Now extract model information from the text provided by the user. If no valid model information can be extracted, return null for all fields.
"""


class ExtractedModel(BaseModel):
    """
    Schema for AI model data extracted by LLM.

    Matches ModelCreate but all fields are optional since
    extraction may not find complete information.
    """

    model_name: str = Field(
        ...,
        description="Technical model identifier",
        examples=["gpt-4", "claude-3-sonnet", "llama-2"],
    )
    organization: str | None = Field(
        None,
        description="Organization that created the model",
        examples=["OpenAI", "Anthropic", "Meta"],
    )
    release_date: date | None = Field(
        None, description="Release date in ISO format (YYYY-MM-DD)"
    )
    description: str = Field(..., description="Brief description of model capabilities")
    license: str | None = Field(
        None,
        description="License type",
        examples=["Apache 2.0", "MIT", "Proprietary", "Other"],
    )


class ExtractionResult(BaseModel):
    """
    Result of an LLM extraction operation.

    Contains the extracted data plus metadata about the extraction
    (tokens used, model, extraction confidence, etc.)
    """

    data: ExtractedModel | None = Field(
        None, description="Extracted model data, or None if no data could be extracted"
    )
    tokens_used: int = Field(description="Total tokens used in the extraction")
    model_used: str = Field(description="Claude model used for extraction")


class LLMService:
    def __init__(self, api_key: str | None = None, model: str | None = DEFAULT_MODEL):
        """
        Initialize the LLM service with Claude API client.

        Args:
            api_key: Anthropic API key. If None, uses settings.anthropic_api_key
            model: Claude model to use. If None, uses DEFAULT_MODEL
        """
        self.api_key = api_key or settings.anthropic_api_key
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not configured. Set ANTHROPIC_API_KEY in .env"
            )

        # Initialize async client
        self.client = AsyncAnthropic(api_key=self.api_key)

        # Default model - Sonnet 4.5 for complex extraction
        self.model = model
        logger.info(f"Initialized LLMService with model: {self.model}")

    async def close(self):
        """Close the API client. Call this in cleanup/shutdown."""
        await self.client.close()

    async def _call_claude_with_retry(
        self,
        system: list[dict],
        messages: list[dict],
        output_format: Type[BaseModel] | None = None,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_tokens: int = 4096,
    ):
        """
        Call Claude API with exponential backoff retry logic.

        Retries on:
        - Rate limit errors (429)
        - Internal server errors (500-599)
        - Connection errors

        Args:
            system: System prompt blocks
            messages: User/assistant messages
            output_format: Pydantic model for structured JSON output
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds (doubles each retry)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Claude API response message (with parsed_output if output_format provided)

        Raises:
            APIError: If all retries are exhausted
        """
        delay = initial_delay

        for attempt in range(max_retries + 1):
            try:
                # Use beta client for structured outputs
                if output_format:
                    response = await self.client.beta.messages.parse(
                        model=self.model,
                        max_tokens=max_tokens,
                        betas=["structured-outputs-2025-11-13"],
                        system=system,
                        messages=messages,
                        output_format=output_format,
                    )
                else:
                    # Regular message creation without structured outputs
                    response = await self.client.messages.create(
                        model=self.model,
                        max_tokens=max_tokens,
                        system=system,
                        messages=messages,
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

    async def extract_model_data(
        self, text: str, use_cache: bool = True
    ) -> ExtractionResult:
        """
        Extract AI model information from unstructured text.

        Uses Claude with structured outputs (JSON outputs) to guarantee
        valid JSON responses matching the ExtractedModel schema.

        Args:
            text: The text to extract model information from
            use_cache: Enable prompt caching to reduce costs (default: True)

        Returns:
            ExtractionResult with extracted data and token usage

        Raises:
            ValueError: If text is empty
        """
        if not text or text.strip() == "":
            raise ValueError("Input text for extraction cannot be empty")

        system_blocks = [
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                # Add ephemeral cache control if use_cache is True
                **({"cache_control": {"type": "ephemeral"}} if use_cache else {}),
            }
        ]

        # Call Claude with retry logic using structured outputs
        try:
            response = await self._call_claude_with_retry(
                system=system_blocks,
                messages=[
                    {
                        "role": "user",
                        "content": f"Extract model information from this text:\n\n{text}",
                    }
                ],
                output_format=ExtractedModel,
            )
        except Exception as e:
            logger.error(f"Failed to extract model data: {e}")
            raise

        # Access the parsed output directly
        extracted_data = response.parsed_output

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
            data=extracted_data, tokens_used=total_tokens, model_used=self.model
        )
