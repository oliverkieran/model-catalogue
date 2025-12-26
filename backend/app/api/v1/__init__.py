"""
API v1 - REST API version 1

Includes:
- Models endpoints: /api/v1/models
- Benchmarks endpoints: /api/v1/benchmarks
"""

from . import models, benchmarks

__all__ = ["models", "benchmarks"]
