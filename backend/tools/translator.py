from __future__ import annotations

from backend.agent.state import CampaignState, add_log


def translate_script(state: CampaignState) -> CampaignState:
    """Mock localization tool.

    Replace this with Gemini Flash-Lite, DeepSeek, DeepL, or another translation API.
    """
    script_data = state.setdefault("script_data", {})
    script_data["translated_target"] = (
        "Ban co thay thong tin vay tai Han Quoc kho hieu khong? "
        "Hay kiem tra dieu kien va giay to can thiet qua kenh chinh thuc. "
        "Kha nang vay co the thay doi tuy theo ket qua tham dinh."
    )

    for scene in script_data.get("scenes", []):
        scene["voiceover_target"] = "[mock Vietnamese] " + scene.get("voiceover_ko", "")
        scene["on_screen_text_target"] = "[mock Vietnamese] " + scene.get("on_screen_text_ko", "")

    return add_log(state, "translator: generated mock localized script")

