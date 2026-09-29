"""
AI Gateway Service Layer.

This module is the single business-logic entry point for all AI features.
API routes call these functions — they never call the gateway or firewall directly.

Responsibilities:
- Enforce RBAC and consent via the privacy firewall.
- Build purpose-limited evidence payloads.
- Call the AI gateway.
- Write audit log entries (metadata only — never raw prompts or responses).
- Map AI exceptions to safe HTTP responses.
- Return typed result schemas.

AI failure is always handled gracefully.  If the AI provider is unavailable,
the rest of ManRakshak continues operating normally.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.exceptions import (
    AIConfigurationError,
    AIGatewayError,
    AIProviderError,
    AIRateLimitError,
    AIResponseValidationError,
    AIUnavailableError,
)
from app.ai.firewall import (
    build_case_evidence_payload,
    build_wellness_evidence_payload,
    enforce_ai_access_policy,
    generate_case_id,
    sanitise_conversation_turns,
)
from app.ai.gateway import get_ai_provider
from app.ai.schemas import (
    ConversationAnalysisResult,
    ReportDraftResult,
    WellnessSummaryResult,
)
from app.ai.privacy import verify_processing_purpose
from app.models.audit import AuditLog
from app.models.enums import AuditAction, ProcessingPurpose, UserRole
from app.models.user import User
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _map_ai_error_to_http(exc: Exception) -> HTTPException:
    """Convert internal AI exceptions to safe HTTP exceptions for clients."""
    if isinstance(exc, AIConfigurationError):
        logger.error("AI configuration error: %s", type(exc).__name__)
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not available due to configuration issues.",
        )
    if isinstance(exc, AIUnavailableError):
        logger.warning("AI provider unavailable: %s", type(exc).__name__)
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is temporarily unavailable. Please try again later.",
        )
    if isinstance(exc, AIRateLimitError):
        logger.warning("AI provider rate limited")
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI service is temporarily rate-limited. Please try again shortly.",
        )
    if isinstance(exc, AIResponseValidationError):
        logger.warning("AI response validation failed: %s", type(exc).__name__)
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service returned an unexpected response. Please try again.",
        )
    if isinstance(exc, AIProviderError):
        logger.warning("AI provider error: %s", type(exc).__name__)
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service encountered an error. Please try again later.",
        )
    # Generic fallback
    logger.error("Unexpected AI error: %s", type(exc).__name__)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the AI service.",
    )


def _log_ai_audit(
    db: Session,
    user_id: str,
    action: AuditAction,
    resource_id: Optional[str] = None,
    resource_type: str = "AI_SERVICE",
    ip_address: Optional[str] = None,
) -> None:
    """
    Write an audit log entry for AI actions.
    NEVER log raw prompts, full responses, API keys, or PII.
    """
    try:
        AuditService.log_action(
            db=db,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
        )
    except Exception as exc:
        # Audit failure must not break the AI call
        logger.warning("Failed to write AI audit log: %s", type(exc).__name__)


# ---------------------------------------------------------------------------
# Conversation Analysis
# ---------------------------------------------------------------------------

async def analyze_conversation_service(
    db: Session,
    current_user: User,
    personnel_id: str,
    conversation_turns: List[Dict[str, str]],
    consent_confirmed: bool,
    request_id: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> ConversationAnalysisResult:
    """
    Analyse a consent-obtained, sanitised wellness conversation.

    Privacy rules:
    - Consent MUST be confirmed explicitly.
    - Personnel can only analyse their own conversation.
    - Welfare officers can analyse personnel in their org.
    - Commander/Admin are blocked.
    - Conversation is sanitised and treated as DATA (injection protection).
    """
    if not consent_confirmed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Explicit consent is required before AI conversation analysis.",
        )

    # RBAC + org isolation
    enforce_ai_access_policy(current_user, personnel_id, db)

    # Consent/governance check
    target_user = db.query(User).filter(User.id == personnel_id).first()
    if not verify_processing_purpose(db, target_user, ProcessingPurpose.AI_CONVERSATION):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI conversation analysis requires consent for AI_CONVERSATION processing purpose.",
        )

    # Audit: AI_ANALYSIS_REQUESTED (metadata only)
    _log_ai_audit(
        db, current_user.id, AuditAction.AI_ANALYSIS_REQUESTED,
        resource_id=personnel_id, resource_type="AI_CONVERSATION",
        ip_address=ip_address,
    )

    # Sanitise conversation (injection protection)
    sanitised_turns = sanitise_conversation_turns(conversation_turns)

    # Call gateway
    try:
        provider = get_ai_provider()
        result = await provider.analyze_conversation(
            sanitised_turns=sanitised_turns,
            request_id=request_id,
        )
    except AIGatewayError as exc:
        # Audit: AI_PROVIDER_ERROR (no sensitive info)
        _log_ai_audit(
            db, current_user.id, AuditAction.AI_PROVIDER_ERROR,
            resource_id=personnel_id, resource_type="AI_CONVERSATION",
            ip_address=ip_address,
        )
        raise _map_ai_error_to_http(exc) from exc

    # Audit: AI_CONVERSATION_ANALYZED (metadata only)
    _log_ai_audit(
        db, current_user.id, AuditAction.AI_CONVERSATION_ANALYZED,
        resource_id=personnel_id, resource_type="AI_CONVERSATION",
        ip_address=ip_address,
    )

    logger.info(
        "Conversation analysis complete [personnel=%s confidence=%s latency=%.0fms]",
        personnel_id,
        result.confidence.value,
        result.latency_ms or 0,
    )

    return result


# ---------------------------------------------------------------------------
# Wellness Summary
# ---------------------------------------------------------------------------

async def generate_wellness_summary_service(
    db: Session,
    current_user: User,
    personnel_id: str,
    request_id: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> WellnessSummaryResult:
    """
    Generate an AI-assisted wellness summary from backend-computed evidence.

    The backend calculates all numeric values (baselines, trends, deviations).
    Only the computed evidence — never raw records — reaches the AI provider.
    """
    # RBAC + org isolation
    enforce_ai_access_policy(current_user, personnel_id, db)

    # Consent/governance check
    target_user = db.query(User).filter(User.id == personnel_id).first()
    if not verify_processing_purpose(db, target_user, ProcessingPurpose.AI_BASELINE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI wellness summary requires consent for AI_BASELINE processing purpose.",
        )

    # Build purpose-limited wellness evidence (no PII, no raw records)
    wellness_evidence = build_wellness_evidence_payload(db, personnel_id)

    # Audit: AI_ANALYSIS_REQUESTED
    _log_ai_audit(
        db, current_user.id, AuditAction.AI_ANALYSIS_REQUESTED,
        resource_id=personnel_id, resource_type="AI_WELLNESS_SUMMARY",
        ip_address=ip_address,
    )

    try:
        provider = get_ai_provider()
        result = await provider.summarize_wellness(
            wellness_evidence=wellness_evidence,
            request_id=request_id,
        )
    except AIGatewayError as exc:
        _log_ai_audit(
            db, current_user.id, AuditAction.AI_PROVIDER_ERROR,
            resource_id=personnel_id, resource_type="AI_WELLNESS_SUMMARY",
            ip_address=ip_address,
        )
        raise _map_ai_error_to_http(exc) from exc

    # Audit: AI_WELLNESS_SUMMARY_GENERATED
    _log_ai_audit(
        db, current_user.id, AuditAction.AI_WELLNESS_SUMMARY_GENERATED,
        resource_id=personnel_id, resource_type="AI_WELLNESS_SUMMARY",
        ip_address=ip_address,
    )

    logger.info(
        "Wellness summary generated [personnel=%s confidence=%s latency=%.0fms]",
        personnel_id,
        result.confidence.value,
        result.latency_ms or 0,
    )

    return result


# ---------------------------------------------------------------------------
# Welfare Report Draft
# ---------------------------------------------------------------------------

async def generate_welfare_report_service(
    db: Session,
    current_user: User,
    personnel_id: str,
    include_conversation_observations: bool = False,
    conversation_observations: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> ReportDraftResult:
    """
    Generate a preliminary welfare/professional-review report draft.

    Flow:
        Personnel data → Privacy Firewall → Backend-computed wellness evidence
        → Optional conversation observations → Qwen → Preliminary report
        → Professional review (human) → Decision → Dashboard update

    Privacy:
        - Personnel identity is replaced with a pseudonymous Case ID.
        - The identity mapping stays inside ManRakshak — never sent to the AI.
        - Only structured observations are included (not raw conversation).
    """
    # RBAC — welfare reports are WELFARE_OFFICER only
    if current_user.role not in (UserRole.WELFARE_OFFICER,):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Welfare Officers can generate welfare report drafts.",
        )

    # Org isolation
    target_user = db.query(User).filter(
        User.id == personnel_id,
        User.organization_id == current_user.organization_id,
    ).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personnel not found within your organisation.",
        )

    # Consent/governance check
    if not verify_processing_purpose(db, target_user, ProcessingPurpose.AI_REPORT):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI report generation requires consent for AI_REPORT processing purpose.",
        )

    # Generate pseudonymous case ID (identity mapping NOT sent to AI)
    case_id = generate_case_id()

    # Build pseudonymous, purpose-limited evidence payload
    case_evidence = build_case_evidence_payload(
        db=db,
        personnel_id=personnel_id,
        case_id=case_id,
        conversation_observations=conversation_observations if include_conversation_observations else None,
    )

    # Audit: AI_ANALYSIS_REQUESTED
    _log_ai_audit(
        db, current_user.id, AuditAction.AI_ANALYSIS_REQUESTED,
        resource_id=personnel_id, resource_type="AI_WELFARE_REPORT",
        ip_address=ip_address,
    )

    try:
        provider = get_ai_provider()
        result = await provider.generate_welfare_report(
            case_evidence=case_evidence,
            request_id=request_id,
        )
    except AIGatewayError as exc:
        _log_ai_audit(
            db, current_user.id, AuditAction.AI_PROVIDER_ERROR,
            resource_id=personnel_id, resource_type="AI_WELFARE_REPORT",
            ip_address=ip_address,
        )
        raise _map_ai_error_to_http(exc) from exc

    # Audit: AI_REPORT_GENERATED (case_id only — not personnel_id)
    _log_ai_audit(
        db, current_user.id, AuditAction.AI_REPORT_GENERATED,
        resource_id=case_id, resource_type="AI_WELFARE_REPORT",
        ip_address=ip_address,
    )

    logger.info(
        "Welfare report draft generated [case_id=%s confidence=%s latency=%.0fms]",
        case_id,
        result.confidence.value,
        result.latency_ms or 0,
    )

    return result
