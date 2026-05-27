from __future__ import annotations

from backend.agent.state import CampaignState, add_log


def match_target(state: CampaignState) -> CampaignState:
    """Mock audience routing and target matching."""
    audience = state.setdefault("target_audience", {})
    nationality = audience.get("nationality", "Unknown")
    visa_type = audience.get("visa_type", "Unknown")

    audience.update(
        {
            "segment": f"{nationality} {visa_type} foreign worker",
            "pain_points": [
                "한국어 금융 용어 이해 어려움",
                "필요서류와 심사 조건 불확실성",
                "불법 대출 광고와 공식 금융 정보 구분 어려움",
            ],
            "message_angle": "공식 채널에서 조건과 필요서류를 먼저 확인하도록 안내",
        }
    )

    return add_log(state, "target_matching: routed audience segment")

