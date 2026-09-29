"""
AI Gateway Provider Interface.

Defines the abstract base class that every AI provider must implement.
The rest of the backend depends ONLY on this interface, never on a concrete
provider.  Swapping from OpenRouter/Qwen to production ML models in the future
requires only a new provider class + updating AI_PROVIDER in .env.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.ai.schemas import (
    AIResponse,
    ConversationAnalysisResult,
    WellnessSummaryResult,
    ReportDraftResult,
)


class AIProvider(ABC):
    """
    Abstract base for all AI/ML providers in ManRakshak.

    Each method returns a typed result schema rather than free-form dicts.
    This contract must be honoured by every concrete implementation so that
    the business layer is fully provider-agnostic.
    """

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_content: str,
        request_id: Optional[str] = None,
    ) -> AIResponse:
        """
        Low-level text generation call.

        The system_prompt carries ManRakshak's strict behavioural constraints.
        user_content is the sanitised, purpose-limited payload — never raw DB
        records and never raw conversation text treated as instructions.

        Returns a structured AIResponse (never arbitrary dicts).
        """
        ...

    @abstractmethod
    async def analyze_conversation(
        self,
        sanitised_turns: List[Dict[str, str]],
        request_id: Optional[str] = None,
    ) -> ConversationAnalysisResult:
        """
        Analyse a consent-obtained, sanitised conversation.

        sanitised_turns is a list of {"role": "user"|"assistant", "content": str}
        dicts.  The content must already have passed through the privacy firewall
        (no names, IDs, ranks, or other PII).

        Returns structured observations only — no diagnoses.
        """
        ...

    @abstractmethod
    async def summarize_wellness(
        self,
        wellness_evidence: Dict[str, Any],
        request_id: Optional[str] = None,
    ) -> WellnessSummaryResult:
        """
        Produce a natural-language summary of backend-computed wellness evidence.

        wellness_evidence must be pre-computed by the backend (baselines, trends,
        deviations).  The AI must not recalculate or invent values.

        Returns a structured WellnessSummaryResult.
        """
        ...

    @abstractmethod
    async def generate_welfare_report(
        self,
        case_evidence: Dict[str, Any],
        request_id: Optional[str] = None,
    ) -> ReportDraftResult:
        """
        Generate a preliminary welfare/professional-review report draft.

        case_evidence is the minimal, purpose-limited payload assembled by the
        backend after passing through the privacy firewall.  The report is
        explicitly preliminary and requires authorized professional review.

        Returns a structured ReportDraftResult.
        """
        ...
