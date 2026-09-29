"""
AI Gateway Exceptions.

Dedicated exception hierarchy for AI Gateway errors.
These are distinct from HTTP exceptions and are mapped to safe HTTP responses
at the API layer so that internal provider details are never leaked to clients.
"""


class AIGatewayError(Exception):
    """Base class for all AI Gateway errors."""
    pass


class AIConfigurationError(AIGatewayError):
    """Raised when the AI provider is misconfigured (e.g. missing API key)."""
    pass


class AIProviderError(AIGatewayError):
    """Raised when the upstream AI provider returns an unexpected error."""
    pass


class AIUnavailableError(AIGatewayError):
    """Raised when the AI provider is unreachable (network/timeout)."""
    pass


class AIResponseValidationError(AIGatewayError):
    """Raised when the AI response cannot be parsed or validated against the schema."""
    pass


class AIRateLimitError(AIGatewayError):
    """Raised when the AI provider rate-limits the request."""
    pass
