"""
AI Gateway Pydantic Schemas.

All AI input/output is validated through these schemas.
No arbitrary dicts flow from the AI layer into the database or dashboard.

IMPORTANT DISCLAIMER
--------------------
The current AI component (Qwen via OpenRouter) is an interim language-processing
assistance layer.  It does NOT perform:
  - Depression diagnosis
  - Burnout diagnosis
  - Validated stress-probability scoring
  - Clinical risk assessment
  - Fitness/unfitness determination
  - Disciplinary assessment

Separately trained and validated predictive models (stress, fatigue, burnout,
depression-risk screening) will be integrated in a future phase through the same
AIProvider interface.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared enumerations
# ---------------------------------------------------------------------------

class EvidenceConfidence(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    INSUFFICIENT = "insufficient"


class ReviewStatus(str, Enum):
    """Status of professional review for a welfare report draft."""
    PENDING_REVIEW = "pending_review"
    UNDER_REVIEW = "under_review"
    REVIEWED = "reviewed"
    CLOSED = "closed"


class ProfessionalDecision(str, Enum):
    """Outcome recorded by the authorized professional after reviewing the AI draft."""
    NO_CONCERN = "no_concern"
    MONITOR = "monitor"
    SUPPORT_RECOMMENDED = "support_recommended"
    REFERRAL_RECOMMENDED = "referral_recommended"


# ---------------------------------------------------------------------------
# Core AI response wrapper
# ---------------------------------------------------------------------------

class AIResponse(BaseModel):
    """
    Thin wrapper around every raw AI provider response.
    Carries metadata needed for observability without exposing sensitive content.
    """
    provider: str = Field(..., description="Provider name, e.g. 'openrouter'")
    model: str = Field(..., description="Model identifier used for this response")
    content: str = Field(..., description="Raw text content returned by the model")
    request_id: Optional[str] = Field(None, description="Provider-side request ID if available")
    latency_ms: Optional[float] = Field(None, description="Round-trip latency in milliseconds")
    success: bool = Field(True)
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings")


# ---------------------------------------------------------------------------
# Conversation analysis schemas
# ---------------------------------------------------------------------------

class ConversationAnalysisResult(BaseModel):
    """
    Structured observations extracted from a consent-obtained wellness conversation.

    These are OBSERVATIONS from the conversation text, not clinical diagnoses.
    Each field reflects what was explicitly reported — the AI must not infer
    unsupported conclusions.
    """
    reported_stressors: List[str] = Field(
        default_factory=list,
        description="Stressors explicitly mentioned by the individual"
    )
    sleep_concern: bool = Field(
        False,
        description="True only if the individual explicitly reported sleep difficulties"
    )
    fatigue_reported: bool = Field(
        False,
        description="True only if the individual explicitly reported fatigue"
    )
    workload_concern: bool = Field(
        False,
        description="True only if the individual explicitly expressed workload concern"
    )
    emotional_themes: List[str] = Field(
        default_factory=list,
        description="Broad emotional themes identified in the conversation (e.g. 'frustration', 'isolation')"
    )
    support_requested: bool = Field(
        False,
        description="True only if the individual explicitly requested or indicated need for support"
    )
    confidence: EvidenceConfidence = Field(
        EvidenceConfidence.LOW,
        description="Confidence in the observations based on evidence in the conversation"
    )
    evidence_summary: str = Field(
        "",
        description="Brief, grounded summary of the supporting evidence"
    )
    insufficient_evidence: bool = Field(
        False,
        description="True when there is not enough conversation content to draw any observation"
    )
    # Latency / audit metadata — not persisted in plain-text form
    provider: Optional[str] = None
    model: Optional[str] = None
    latency_ms: Optional[float] = None


# ---------------------------------------------------------------------------
# Wellness summary schemas
# ---------------------------------------------------------------------------

class SignalSummary(BaseModel):
    """AI-generated textual summary of a single wellness signal."""
    signal: str
    observation: str = Field(description="What the AI observed about this signal based on supplied evidence")
    trend_noted: Optional[str] = Field(None, description="Trend direction noted by the AI, if evidence supplied")


class WellnessSummaryResult(BaseModel):
    """
    AI-generated narrative summary of backend-computed wellness evidence.

    The backend computes all numeric values (baselines, trends, deviations).
    The AI translates those into natural language.  It must NOT recalculate
    or invent values not present in the evidence payload.
    """
    overall_observation: str = Field(
        description="High-level, evidence-grounded wellness observation"
    )
    signal_summaries: List[SignalSummary] = Field(
        default_factory=list,
        description="Per-signal observations"
    )
    confidence: EvidenceConfidence
    evidence_summary: str = Field(
        description="Brief description of the evidence quality used"
    )
    professional_review_recommended: bool = Field(
        False,
        description="True when the AI recommends professional welfare review based on supplied evidence"
    )
    data_quality_note: Optional[str] = Field(
        None,
        description="Note about data quality if evidence was sparse"
    )
    disclaimer: str = Field(
        default=(
            "This is an AI-assisted summary based on supplied wellness data. "
            "It is not a medical diagnosis. Professional review is required for "
            "any welfare decision."
        )
    )
    provider: Optional[str] = None
    model: Optional[str] = None
    latency_ms: Optional[float] = None


# ---------------------------------------------------------------------------
# Welfare report draft schemas (pseudonymous case)
# ---------------------------------------------------------------------------

class ReportSection(BaseModel):
    """A single section of the welfare report draft."""
    title: str
    content: str


class ReportDraftResult(BaseModel):
    """
    Preliminary welfare/professional-review report draft generated by the AI.

    This draft is explicitly preliminary.  It MUST be reviewed by an
    authorized human professional before any welfare decision is made.

    NOTE: The case_id is a pseudonymous identifier (e.g. MR-7F29K4).
    The identity mapping is maintained securely inside ManRakshak and
    must NOT be exposed in AI prompts or in this schema.
    """
    case_id: str = Field(description="Pseudonymous case identifier")
    report_version: str = Field("1.0", description="Report schema version")
    sections: List[ReportSection] = Field(
        default_factory=list,
        description="Structured sections of the preliminary report"
    )
    overall_observation: str = Field(
        description="AI-generated high-level observation based on supplied evidence"
    )
    confidence: EvidenceConfidence
    evidence_summary: str
    professional_review_recommended: bool = Field(True)  # Always true for reports
    ai_generated_at: Optional[str] = Field(
        None,
        description="ISO 8601 timestamp of AI generation (not the professional review)"
    )
    disclaimer: str = Field(
        default=(
            "IMPORTANT: This is a preliminary AI-assisted summary for professional "
            "welfare review only. It is NOT a medical diagnosis, clinical assessment, "
            "or fitness/unfitness determination. The final professional decision "
            "belongs exclusively to the authorized human welfare professional."
        )
    )
    provider: Optional[str] = None
    model: Optional[str] = None
    latency_ms: Optional[float] = None


# ---------------------------------------------------------------------------
# Professional review record (future doctor-portal integration)
# ---------------------------------------------------------------------------

class ProfessionalReviewRecord(BaseModel):
    """
    Represents the professional review and decision recorded against a report draft.
    This schema is used internally by the backend for future doctor-portal integration.
    It is NOT populated automatically by the AI.
    """
    case_id: str
    report_version: str
    review_status: ReviewStatus = ReviewStatus.PENDING_REVIEW
    professional_review: Optional[str] = Field(
        None,
        description="Free-text professional assessment (entered by authorized human)"
    )
    professional_decision: Optional[ProfessionalDecision] = Field(
        None,
        description="Structured professional outcome"
    )
    reviewed_at: Optional[str] = Field(
        None,
        description="ISO 8601 timestamp of professional review"
    )
    reviewed_by_role: Optional[str] = Field(
        None,
        description="Role of the reviewing professional (no personal identity stored here)"
    )


# ---------------------------------------------------------------------------
# API request/response schemas for AI endpoints
# ---------------------------------------------------------------------------

class ConversationAnalyzeRequest(BaseModel):
    """Request body for POST /api/v1/ai/conversation/analyze"""
    personnel_id: str = Field(
        description="ID of the personnel whose conversation is being analyzed (must match auth context)"
    )
    conversation_turns: List[Dict[str, str]] = Field(
        description=(
            "Sanitised conversation turns. Each turn must have 'role' (user|assistant) "
            "and 'content'. Content is treated as DATA, not as instructions."
        ),
        min_length=1,
        max_length=50,
    )
    consent_confirmed: bool = Field(
        description="Must be True — confirms explicit consent for AI conversation analysis"
    )


class WellnessSummaryRequest(BaseModel):
    """Request body for POST /api/v1/ai/wellness/summary"""
    personnel_id: str = Field(
        description="ID of the personnel (must match auth context)"
    )


class ReportDraftRequest(BaseModel):
    """Request body for POST /api/v1/ai/report/draft"""
    personnel_id: str = Field(
        description=(
            "ID of the personnel. The backend will pseudonymize before sending to AI."
        )
    )
    include_conversation_observations: bool = Field(
        False,
        description="Include latest consent-obtained conversation observations in the report"
    )
