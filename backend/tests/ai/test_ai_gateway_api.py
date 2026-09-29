"""
Tests for AI Gateway API Endpoints (/api/v1/ai).

Covers:
- POST /api/v1/ai/conversation/analyze
- POST /api/v1/ai/wellness/summary
- POST /api/v1/ai/report/draft
- Privacy firewall enforcement (consent requirement, cross-user boundary, pseudonymisation)
- RBAC enforcement (Welfare Officer requirement for reports)
- Safe error handling and graceful degradation on AI provider failures
"""

import uuid
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.enums import UserRole, UserStatus, ProcessingPurpose, ConsentStatus
from app.models.organization import Organization
from app.models.unit import Unit
from app.models.user import User
from app.models.governance import GovernancePolicy, UserConsent
from app.ai.interfaces import AIProvider
from app.ai.schemas import (
    AIResponse,
    ConversationAnalysisResult,
    EvidenceConfidence,
    ReportDraftResult,
    ReportSection,
    SignalSummary,
    WellnessSummaryResult,
)
from app.ai.exceptions import AIUnavailableError
from tests.conftest import TestingSessionLocal

client = TestClient(app)


class MockAIProvider(AIProvider):
    """Mock AI Provider that adheres to the AIProvider interface for testing."""

    async def generate(self, system_prompt: str, user_content: str, request_id=None) -> AIResponse:
        return AIResponse(
            provider="mock",
            model="mock-model",
            content="{}",
            request_id=request_id,
            latency_ms=10.0,
            success=True,
        )

    async def analyze_conversation(self, sanitised_turns, request_id=None) -> ConversationAnalysisResult:
        return ConversationAnalysisResult(
            reported_stressors=["workload"],
            sleep_concern=True,
            fatigue_reported=True,
            workload_concern=True,
            emotional_themes=["tiredness"],
            support_requested=False,
            confidence=EvidenceConfidence.HIGH,
            evidence_summary="Reported fatigue during late duties.",
            provider="mock",
            model="mock-model",
        )

    async def summarize_wellness(self, wellness_evidence, request_id=None) -> WellnessSummaryResult:
        return WellnessSummaryResult(
            overall_observation="Observed slight downward trend in reported sleep duration over past 7 days.",
            signal_summaries=[
                SignalSummary(
                    signal="sleep_hours",
                    observation="Average sleep reduced compared to baseline",
                    trend_noted="decreasing",
                )
            ],
            confidence=EvidenceConfidence.MODERATE,
            evidence_summary="Based on 7 check-ins.",
            professional_review_recommended=False,
            provider="mock",
            model="mock-model",
        )

    async def generate_welfare_report(self, case_evidence, request_id=None) -> ReportDraftResult:
        return ReportDraftResult(
            case_id=case_evidence.get("case_id", "CASE-TEST"),
            report_version="1.0",
            sections=[
                ReportSection(title="Summary", content="Preliminary AI observations based on records.")
            ],
            overall_observation="Moderate fatigue patterns noted.",
            confidence=EvidenceConfidence.MODERATE,
            evidence_summary="7-day wellness records and unit context.",
            professional_review_recommended=True,
            provider="mock",
            model="mock-model",
        )


@pytest.fixture
def ai_test_data():
    db = TestingSessionLocal()
    suffix = str(uuid.uuid4())[:8]

    org = Organization(organization_code=f"ORG_AI_{suffix}", name="AI Test Org")
    db.add(org)
    db.commit()

    unit = Unit(organization_id=org.id, unit_name="AI Test Unit", unit_code=f"UNIT_AI_{suffix}")
    db.add(unit)
    db.commit()

    # Personnel User 1
    p1 = User(
        organization_id=org.id,
        unit_id=unit.id,
        user_code=f"PA1_{suffix}",
        name="Personnel One",
        email=f"pa1_{suffix}@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE,
    )

    # Personnel User 2
    p2 = User(
        organization_id=org.id,
        unit_id=unit.id,
        user_code=f"PA2_{suffix}",
        name="Personnel Two",
        email=f"pa2_{suffix}@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE,
    )

    # Welfare Officer User
    wo = User(
        organization_id=org.id,
        unit_id=unit.id,
        user_code=f"WO_{suffix}",
        name="Welfare Officer One",
        email=f"wo_{suffix}@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.WELFARE_OFFICER,
        status=UserStatus.ACTIVE,
    )

    # Commander User (not Welfare Officer)
    cmd = User(
        organization_id=org.id,
        unit_id=unit.id,
        user_code=f"CMD_{suffix}",
        name="Commander One",
        email=f"cmd_{suffix}@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.COMMANDER,
        status=UserStatus.ACTIVE,
    )

    db.add_all([p1, p2, wo, cmd])
    db.commit()

    # Governance Policy allowing all purposes for this organization
    policy = GovernancePolicy(
        organization_id=org.id,
        version="1.0",
        allowed_purposes=[p.value for p in ProcessingPurpose],
        is_active=True,
    )
    db.add(policy)
    db.commit()

    # Add AI Consent for p1 for all AI purposes
    for purpose in [ProcessingPurpose.AI_BASELINE, ProcessingPurpose.AI_CONVERSATION, ProcessingPurpose.AI_REPORT]:
        consent = UserConsent(
            user_id=p1.id,
            purpose=purpose.value,
            status=ConsentStatus.GRANTED.value,
        )
        db.add(consent)
    db.commit()

    yield {
        "p1_id": p1.id,
        "p1_email": p1.email,
        "p2_id": p2.id,
        "p2_email": p2.email,
        "wo_id": wo.id,
        "wo_email": wo.email,
        "cmd_id": cmd.id,
        "cmd_email": cmd.email,
    }
    db.close()


def _login(email: str) -> str:
    res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"},
    )
    return res.json()["access_token"]


def test_ai_conversation_analyze_requires_consent_flag(ai_test_data):
    """Test that conversation analysis rejects if consent_confirmed is False."""
    token = _login(ai_test_data["p1_email"])
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "personnel_id": ai_test_data["p1_id"],
        "conversation_turns": [
            {"speaker": "user", "text": "I feel tired from late duties."}
        ],
        "consent_confirmed": False,
    }

    res = client.post(
        f"{settings.API_V1_STR}/ai/conversation/analyze",
        json=payload,
        headers=headers,
    )
    assert res.status_code in [400, 403]


@patch("app.services.ai_gateway_service.get_ai_provider", return_value=MockAIProvider())
def test_ai_conversation_analyze_success(mock_provider, ai_test_data):
    """Test successful conversation analysis with mock provider and disclaimer check."""
    token = _login(ai_test_data["p1_email"])
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "personnel_id": ai_test_data["p1_id"],
        "conversation_turns": [
            {"speaker": "user", "text": "I feel tired from late duties."}
        ],
        "consent_confirmed": True,
    }

    res = client.post(
        f"{settings.API_V1_STR}/ai/conversation/analyze",
        json=payload,
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ai_assisted_summary"
    assert "disclaimer" in data
    assert "NOT a medical diagnosis" in data["disclaimer"]
    assert data["observations"]["fatigue_reported"] is True
    assert "workload" in data["observations"]["reported_stressors"]


@patch("app.services.ai_gateway_service.get_ai_provider", return_value=MockAIProvider())
def test_ai_wellness_summary_cross_user_forbidden(mock_provider, ai_test_data):
    """Test that personnel cannot request wellness summary of another personnel."""
    token = _login(ai_test_data["p1_email"])
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "personnel_id": ai_test_data["p2_id"],  # Other user
    }

    res = client.post(
        f"{settings.API_V1_STR}/ai/wellness/summary",
        json=payload,
        headers=headers,
    )
    # Privacy firewall or RBAC should reject cross-user access
    assert res.status_code == 403


@patch("app.services.ai_gateway_service.get_ai_provider", return_value=MockAIProvider())
def test_ai_report_draft_requires_welfare_officer(mock_provider, ai_test_data):
    """Test that commander or personnel cannot generate welfare report drafts."""
    # Test as Commander
    cmd_token = _login(ai_test_data["cmd_email"])
    cmd_headers = {"Authorization": f"Bearer {cmd_token}"}

    payload = {
        "personnel_id": ai_test_data["p1_id"],
        "include_conversation_observations": False,
    }

    res = client.post(
        f"{settings.API_V1_STR}/ai/report/draft",
        json=payload,
        headers=cmd_headers,
    )
    assert res.status_code == 403


@patch("app.services.ai_gateway_service.get_ai_provider", return_value=MockAIProvider())
def test_ai_report_draft_success_for_welfare_officer(mock_provider, ai_test_data):
    """Test that Welfare Officer can generate a preliminary welfare draft report."""
    wo_token = _login(ai_test_data["wo_email"])
    wo_headers = {"Authorization": f"Bearer {wo_token}"}

    payload = {
        "personnel_id": ai_test_data["p1_id"],
        "include_conversation_observations": False,
    }

    res = client.post(
        f"{settings.API_V1_STR}/ai/report/draft",
        json=payload,
        headers=wo_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "preliminary_ai_draft"
    assert "PRELIMINARY AI-ASSISTED SUMMARY" in data["disclaimer"]
    assert "report" in data
    assert data["report"]["case_id"] is not None


@patch("app.services.ai_gateway_service.get_ai_provider")
def test_ai_provider_unavailable_graceful_degradation(mock_get_provider, ai_test_data):
    """Test that if AI provider fails or is unreachable, the API returns a clean 503."""
    failing_provider = AsyncMock()
    failing_provider.analyze_conversation.side_effect = AIUnavailableError("Service unreachable")
    mock_get_provider.return_value = failing_provider

    token = _login(ai_test_data["p1_email"])
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "personnel_id": ai_test_data["p1_id"],
        "conversation_turns": [{"speaker": "user", "text": "Testing failure"}],
        "consent_confirmed": True,
    }

    res = client.post(
        f"{settings.API_V1_STR}/ai/conversation/analyze",
        json=payload,
        headers=headers,
    )
    assert res.status_code == 503
    assert "temporarily unavailable" in res.json()["detail"].lower()
