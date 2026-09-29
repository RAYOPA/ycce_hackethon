"""
ManRakshak AI Module.

Architecture:
    FastAPI → AI Gateway (gateway.py) → OpenRouter Provider → Qwen

Current interim AI assistance layer (NOT predictive ML):
    Provider:  OpenRouter
    Model:     qwen/qwen3.8-27b:free (configurable via OPEN_ROUTER_MODEL)

Future:
    Production predictive ML models (stress, fatigue, burnout, depression-risk)
    will implement the AIProvider interface (interfaces.py) and be registered
    in gateway.py without changes to business logic.

Key modules:
    gateway.py    — Provider factory and selection (AI_PROVIDER in .env)
    interfaces.py — Abstract AIProvider contract
    schemas.py    — Typed input/output schemas (no arbitrary dicts to DB)
    exceptions.py — AI-specific exception hierarchy
    firewall.py   — Privacy firewall (data minimisation before AI calls)
    providers/    — Concrete provider implementations
    prompts/      — System prompts with strict behavioural constraints
"""

from app.ai.exceptions import (
    AIConfigurationError,
    AIGatewayError,
    AIProviderError,
    AIRateLimitError,
    AIResponseValidationError,
    AIUnavailableError,
)
from app.ai.gateway import get_ai_provider, reset_provider_for_testing

__all__ = [
    "get_ai_provider",
    "reset_provider_for_testing",
    "AIGatewayError",
    "AIConfigurationError",
    "AIProviderError",
    "AIUnavailableError",
    "AIResponseValidationError",
    "AIRateLimitError",
]
