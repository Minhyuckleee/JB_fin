from __future__ import annotations

from backend.agent.state import CampaignState, add_log


PROHIBITED_TERMS = ["무조건", "누구나", "즉시 확정", "100% 승인", "최저금리 보장"]


def check_compliance(state: CampaignState, stage: str = "script") -> CampaignState:
    """Mock compliance and fact checker."""
    script_data = state.get("script_data", {})
    text_parts = [script_data.get("original_korean", ""), script_data.get("translated_target", "")]
    for scene in script_data.get("scenes", []):
        text_parts.extend(
            [
                scene.get("voiceover_ko", ""),
                scene.get("voiceover_target", ""),
                scene.get("on_screen_text_ko", ""),
                scene.get("on_screen_text_target", ""),
            ]
        )
    full_text = " ".join(text_parts)

    issues = []
    for term in PROHIBITED_TERMS:
        if term in full_text:
            issues.append(
                {
                    "type": "prohibited_claim",
                    "text": term,
                    "reason": "대출 승인 또는 조건을 확정적으로 오인시킬 수 있음",
                    "suggested_revision": "대출 가능 여부는 심사 결과에 따라 달라질 수 있습니다.",
                }
            )

    state.setdefault("compliance_reports", []).append(
        {
            "status": "needs_revision" if issues else "approved",
            "checked_stage": stage,
            "issues": issues,
            "evidence_checks": [
                {
                    "claim": "대출 가능 여부는 심사 결과에 따라 달라질 수 있음",
                    "status": "supported",
                    "citation_ids": [c["citation_id"] for c in state.get("rag_citations", [])],
                }
            ],
        }
    )
    return add_log(state, f"compliance_checker: checked {stage}, issues={len(issues)}")

