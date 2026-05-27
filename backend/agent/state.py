from __future__ import annotations

from typing import Any, Literal, TypedDict


ComplianceStatus = Literal["not_checked", "approved", "needs_revision"]


class TargetAudience(TypedDict, total=False):
    nationality: str
    visa_type: str
    occupation: str
    language: str
    segment: str
    pain_points: list[str]
    message_angle: str


class ProductInfo(TypedDict, total=False):
    product_name: str
    campaign_goal: str
    interest_rate: str | None
    limit: str | None
    compliance_constraints: list[str]


class Citation(TypedDict, total=False):
    citation_id: str
    source: str
    page: int | None
    text: str
    score: float


class Scene(TypedDict, total=False):
    scene_id: int
    duration_sec: float
    scene: str
    voiceover_ko: str
    voiceover_target: str
    on_screen_text_ko: str
    on_screen_text_target: str
    visual_prompt: str
    citations: list[str]
    cta: bool


class ScriptData(TypedDict, total=False):
    total_estimated_duration_sec: float
    original_korean: str
    translated_target: str
    scenes: list[Scene]


class MediaAssets(TypedDict, total=False):
    tts_audio_url: str | None
    image_urls: list[str]
    subtitle_path: str | None
    video_path: str | None
    word_timestamps: list[dict[str, Any]]


class ComplianceIssue(TypedDict, total=False):
    type: str
    text: str
    reason: str
    suggested_revision: str


class ComplianceReport(TypedDict, total=False):
    status: ComplianceStatus
    checked_stage: str
    issues: list[ComplianceIssue]
    evidence_checks: list[dict[str, Any]]


class CampaignState(TypedDict, total=False):
    campaign_id: str
    target_audience: TargetAudience
    product_info: ProductInfo
    raw_documents: list[str]
    parsed_documents: list[dict[str, Any]]
    rag_citations: list[Citation]
    script_data: ScriptData
    media_assets: MediaAssets
    compliance_reports: list[ComplianceReport]
    logs: list[str]


def create_initial_state() -> CampaignState:
    """Return a sample state for local mock runs."""
    return {
        "campaign_id": "demo-campaign-001",
        "target_audience": {
            "nationality": "Vietnam",
            "visa_type": "E-9",
            "occupation": "factory worker",
            "language": "Vietnamese",
        },
        "product_info": {
            "product_name": "Foreign resident loan guidance",
            "campaign_goal": "생활자금 대출 정보를 쉽고 안전하게 안내",
            "interest_rate": None,
            "limit": None,
            "compliance_constraints": [
                "대출 가능 여부는 심사 결과에 따라 달라질 수 있음",
                "무조건 승인, 누구나 가능, 즉시 확정 표현 금지",
            ],
        },
        "raw_documents": ["sample_product_guide.pdf"],
        "parsed_documents": [],
        "rag_citations": [],
        "script_data": {},
        "media_assets": {
            "tts_audio_url": None,
            "image_urls": [],
            "subtitle_path": None,
            "video_path": None,
            "word_timestamps": [],
        },
        "compliance_reports": [],
        "logs": [],
    }


def add_log(state: CampaignState, message: str) -> CampaignState:
    state.setdefault("logs", []).append(message)
    return state

