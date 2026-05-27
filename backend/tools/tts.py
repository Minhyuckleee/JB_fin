from __future__ import annotations

from backend.agent.state import CampaignState, add_log


def generate_tts(state: CampaignState) -> CampaignState:
    """Mock TTS generation."""
    media_assets = state.setdefault("media_assets", {})
    media_assets["tts_audio_url"] = "mock://audio/voiceover.mp3"
    return add_log(state, "tts: generated mock audio asset")

