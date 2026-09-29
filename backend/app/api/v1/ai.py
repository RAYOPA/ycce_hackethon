"""
AI Gateway API Router — v1 endpoints.

Endpoints:
    POST /api/v1/ai/conversation/analyze  — Consent-based conversation analysis
    POST /api/v1/ai/wellness/summary      — AI-assisted wellness summary
    POST /api/v1/ai/report/draft          — Preliminary welfare report draft (WO only)

All endpoints use existing:
    - Authentication (get_current_user / require_*)
    - RBAC (role-based dependency injection)
    - Organisation isolation (enforced in ai_gateway_service)
    - Privacy firewall (enforced before AI call)
    - Audit logging (in ai_gateway_service)

IMPORTANT — Language compliance:
    These endpoints return AI-ASSISTED summaries and preliminary observations.
    They do NOT claim to detect depression, burnout, or clinical risk.
    Professional review is always required for welfare decisions.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_welfare_officer
from app.core.database import get_db
from app.models.user import User
from app.schemas.ai import (
    ConversationAnalyzeRequest,
    ConversationAnalyzeResponse,
    ReportDraftRequest,
    ReportDraftResponse,
    WellnessSummaryRequest,
    WellnessSummaryResponse,
)
from app.services.ai_gateway_service import (
    analyze_conversation_service,
    generate_welfare_report_service,
    generate_wellness_summary_service,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /ai/conversation/analyze
# ---------------------------------------------------------------------------

@router.post(
    "/conversation/analyze",
    response_model=ConversationAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="AI-Assisted Conversation Analysis (Consent Required)",
    description=(
        "Extracts structured observations from a consent-obtained wellness conversation. "
        "Returns reported observations only — NOT a medical diagnosis. "
        "Professional review is required before any welfare decision. "
        "Requires explicit consent_confirmed=true in the request body."
    ),
)
async def analyze_conversation(
    request_body: ConversationAnalyzeRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversationAnalyzeResponse:
    ip_address = request.client.host if request and request.client else None
    request_id = getattr(request.state, "request_id", None)

    result = await analyze_conversation_service(
        db=db,
        current_user=current_user,
        personnel_id=request_body.personnel_id,
        conversation_turns=request_body.conversation_turns,
        consent_confirmed=request_body.consent_confirmed,
        request_id=request_id,
        ip_address=ip_address,
    )

    return ConversationAnalyzeResponse(
        status="ai_assisted_summary",
        disclaimer=(
            "These are AI-extracted observations from the conversation. "
            "This is NOT a medical diagnosis. Professional review is required."
        ),
        observations=result,
    )


# ---------------------------------------------------------------------------
# POST /ai/wellness/summary
# ---------------------------------------------------------------------------

@router.post(
    "/wellness/summary",
    response_model=WellnessSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="AI-Assisted Wellness Summary",
    description=(
        "Generates a natural-language summary of backend-computed wellness evidence. "
        "The AI explains trends in the supplied data — it does not diagnose. "
        "Returns a preliminary observation requiring professional review."
    ),
)
async def wellness_summary(
    request_body: WellnessSummaryRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WellnessSummaryResponse:
    ip_address = request.client.host if request and request.client else None
    request_id = getattr(request.state, "request_id", None)

    result = await generate_wellness_summary_service(
        db=db,
        current_user=current_user,
        personnel_id=request_body.personnel_id,
        request_id=request_id,
        ip_address=ip_address,
    )

    return WellnessSummaryResponse(
        status="ai_assisted_summary",
        disclaimer=(
            "This is an AI-assisted summary based on supplied wellness data. "
            "It is NOT a medical diagnosis. Professional review is required."
        ),
        summary=result,
    )


# ---------------------------------------------------------------------------
# POST /ai/report/draft
# ---------------------------------------------------------------------------

@router.post(
    "/report/draft",
    response_model=ReportDraftResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Preliminary Welfare Report Draft (Welfare Officer Only)",
    description=(
        "Generates a preliminary AI-assisted welfare report for professional review. "
        "Personnel identity is pseudonymised before being sent to the AI provider. "
        "REQUIRES Welfare Officer role. "
        "This draft is NOT a medical diagnosis or fitness determination — "
        "professional review is mandatory before any welfare decision."
    ),
)
async def report_draft(
    request_body: ReportDraftRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_welfare_officer),
) -> ReportDraftResponse:
    ip_address = request.client.host if request and request.client else None
    request_id = getattr(request.state, "request_id", None)

    result = await generate_welfare_report_service(
        db=db,
        current_user=current_user,
        personnel_id=request_body.personnel_id,
        include_conversation_observations=request_body.include_conversation_observations,
        request_id=request_id,
        ip_address=ip_address,
    )

    return ReportDraftResponse(
        status="preliminary_ai_draft",
        disclaimer=(
            "PRELIMINARY AI-ASSISTED SUMMARY — FOR PROFESSIONAL REVIEW ONLY. "
            "This is NOT a medical diagnosis, clinical assessment, or "
            "fitness/unfitness determination. The final professional decision "
            "belongs exclusively to the authorised human welfare professional."
        ),
        report=result,
    )
