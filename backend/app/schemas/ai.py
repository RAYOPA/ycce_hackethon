"""
Pydantic schemas for the AI API endpoints.

These are the request/response schemas exposed to API clients.
They wrap the internal AI result schemas with appropriate disclaimers
and status fields to ensure consistent, honest language.

IMPORTANT:
    No schema here claims:
    - AI detected depression / burnout / stress probability
    - AI diagnosed any condition
    - AI determined fitness / unfitness
    - AI approved / rejected a person

    All AI outputs are presented as:
    - "AI-assisted summary"
    - "Preliminary observation"
    - "Professional review required"
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.ai.schemas import (
    ConversationAnalysisResult,
    ReportDraftResult,
    WellnessSummaryResult,
)


# ---------------------------------------------------------------------------
# Request schemas (re-exported from ai.schemas for API layer use)
# ---------------------------------------------------------------------------

class ConversationAnalyzeRequest(BaseModel):
    """Request body for POST /api/v1/ai/conversation/analyze"""
    personnel_id: str = Field(
        description="ID of the personnel whose conversation is being analyzed"
    )
    conversation_turns: List[Dict[str, str]] = Field(
        description=(
            "Sanitised conversation turns. Each must have 'role' and 'content'. "
            "Content is treated as DATA — not as instructions."
        ),
        min_length=1,
        max_length=50,
    )
    consent_confirmed: bool = Field(
        description="Must be True — explicit consent for AI conversation analysis"
    )


class WellnessSummaryRequest(BaseModel):
    """Request body for POST /api/v1/ai/wellness/summary"""
    personnel_id: str = Field(
        description="ID of the personnel (must match your own ID unless you are a Welfare Officer)"
    )


class ReportDraftRequest(BaseModel):
    """Request body for POST /api/v1/ai/report/draft (Welfare Officer only)"""
    personnel_id: str = Field(
        description="ID of the personnel for whom to generate the welfare report draft"
    )
    include_conversation_observations: bool = Field(
        False,
        description=(
            "Include latest consent-obtained, structured conversation observations "
            "in the report (NOT raw conversation)"
        ),
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class ConversationAnalyzeResponse(BaseModel):
    """Response for POST /api/v1/ai/conversation/analyze"""
    status: str = Field(
        "ai_assisted_summary",
        description="Always 'ai_assisted_summary' — never a diagnosis",
    )
    disclaimer: str = Field(
        description="Clear disclaimer that this is not a medical diagnosis"
    )
    observations: ConversationAnalysisResult = Field(
        description="Structured observations extracted from the conversation"
    )


class WellnessSummaryResponse(BaseModel):
    """Response for POST /api/v1/ai/wellness/summary"""
    status: str = Field(
        "ai_assisted_summary",
        description="Always 'ai_assisted_summary' — never a diagnosis",
    )
    disclaimer: str = Field(
        description="Clear disclaimer that this is not a medical diagnosis"
    )
    summary: WellnessSummaryResult = Field(
        description="AI-assisted wellness summary based on supplied evidence"
    )


class ReportDraftResponse(BaseModel):
    """Response for POST /api/v1/ai/report/draft"""
    status: str = Field(
        "preliminary_ai_draft",
        description="Always 'preliminary_ai_draft' — requires professional review",
    )
    disclaimer: str = Field(
        description=(
            "Clear disclaimer that this is a preliminary draft requiring "
            "professional review, not a medical diagnosis"
        )
    )
    report: ReportDraftResult = Field(
        description="Preliminary welfare report draft for professional review"
    )
