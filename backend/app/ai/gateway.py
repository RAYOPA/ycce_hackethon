"""
AI Gateway — provider factory and central entry point.

Business logic in the rest of the backend uses this module only.
No other module should import from app.ai.providers directly.

Current routing (AI_PROVIDER=openrouter):
    FastAPI → AI Gateway → OpenRouter → Qwen (qwen/qwen3.8-27b:free)

Future routing (change AI_PROVIDER in .env):
    FastAPI → AI Gateway → Production ML models / other providers

ADDING A FUTURE PROVIDER:
1. Create app/ai/providers/<name>.py implementing AIProvider.
2. Register it in the _PROVIDER_REGISTRY dict below.
3. Set AI_PROVIDER=<name> in .env.
No changes to business logic or API routes are required.
"""

import logging
from typing import Dict, Type

from app.ai.exceptions import AIConfigurationError, AIGatewayError
from app.ai.interfaces import AIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Provider registry — maps AI_PROVIDER values to concrete classes
# ---------------------------------------------------------------------------

def _build_registry() -> Dict[str, Type[AIProvider]]:
    """
    Lazily import provider classes to avoid hard dependencies at module load time.
    Missing optional dependencies (e.g. httpx) will only error at instantiation.
    """
    from app.ai.providers.openrouter import OpenRouterProvider

    return {
        "openrouter": OpenRouterProvider,
        # Future providers registered here:
        # "stress_ml": StressMLProvider,
        # "internal": InternalMLProvider,
    }


_provider_instance: AIProvider | None = None


def get_ai_provider() -> AIProvider:
    """
    Return the configured AI provider singleton.

    Thread-safety note: In production FastAPI (async, single-process) this is
    safe.  For multi-process deployments, each process maintains its own instance.

    Raises AIConfigurationError if the provider is unknown or mis-configured.
    Raises AIGatewayError subclasses for other initialisation failures.
    """
    global _provider_instance

    if _provider_instance is not None:
        return _provider_instance

    provider_name = settings.AI_PROVIDER.lower().strip()
    registry = _build_registry()

    if provider_name not in registry:
        available = ", ".join(sorted(registry.keys()))
        raise AIConfigurationError(
            f"Unknown AI_PROVIDER '{provider_name}'. Available: {available}"
        )

    provider_class = registry[provider_name]

    try:
        _provider_instance = provider_class()
        logger.info(
            "AI Gateway initialised with provider='%s' model='%s'",
            provider_name,
            getattr(settings, "OPEN_ROUTER_MODEL", "N/A"),
        )
        return _provider_instance
    except AIGatewayError:
        raise
    except Exception as exc:
        raise AIConfigurationError(
            f"Failed to initialise AI provider '{provider_name}'"
        ) from exc


def reset_provider_for_testing() -> None:
    """
    Clear the cached provider instance.
    ONLY for use in test fixtures — never call in production code.
    """
    global _provider_instance
    _provider_instance = None
