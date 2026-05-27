from __future__ import annotations

from backend.agent.state import CampaignState, add_log


def generate_script(state: CampaignState) -> CampaignState:
    """Mock short-form script generator."""
    citations = [item["citation_id"] for item in state.get("rag_citations", [])]
    state["script_data"] = {
        "total_estimated_duration_sec": 15.0,
        "original_korean": (
            "한국에서 대출 정보가 헷갈리시나요? 공식 채널에서 조건과 "
            "필요 서류를 먼저 확인하세요. 대출 가능 여부는 심사 결과에 따라 달라질 수 있습니다."
        ),
        "scenes": [
            {
                "scene_id": 1,
                "duration_sec": 5.0,
                "scene": "외국인 근로자가 휴대폰에서 대출 광고를 보고 고민한다.",
                "voiceover_ko": "한국에서 대출 정보가 헷갈리시나요?",
                "on_screen_text_ko": "대출 정보, 어디서 확인할까요?",
                "visual_prompt": "friendly animated foreign worker looking at a phone, no text",
                "citations": citations,
                "cta": False,
            },
            {
                "scene_id": 2,
                "duration_sec": 5.0,
                "scene": "공식 금융 채널을 확인하는 화면.",
                "voiceover_ko": "공식 채널에서 조건과 필요 서류를 먼저 확인하세요.",
                "on_screen_text_ko": "공식 채널에서 조건 확인",
                "visual_prompt": "clean mobile banking information screen, no logo, no text",
                "citations": citations,
                "cta": True,
            },
            {
                "scene_id": 3,
                "duration_sec": 5.0,
                "scene": "안내 문구와 상담 CTA가 나타난다.",
                "voiceover_ko": "대출 가능 여부는 심사 결과에 따라 달라질 수 있습니다.",
                "on_screen_text_ko": "심사 결과에 따라 달라질 수 있어요",
                "visual_prompt": "simple animated guidance card, trustworthy financial mood, no text",
                "citations": citations,
                "cta": True,
            },
        ],
    }
    return add_log(state, "script_generator: generated mock short-form script")

