from __future__ import annotations

from backend.agent.state import CampaignState, add_log


def generate_subtitles(state: CampaignState) -> CampaignState:
    """Mock subtitle generation."""
    timestamps = []
    cursor = 0.0
    for scene in state.get("script_data", {}).get("scenes", []):
        duration = float(scene.get("duration_sec", 0.0))
        timestamps.append(
            {
                "scene_id": scene.get("scene_id"),
                "start_sec": cursor,
                "end_sec": cursor + duration,
                "text": scene.get("on_screen_text_ko", ""),
            }
        )
        cursor += duration

    media_assets = state.setdefault("media_assets", {})
    media_assets["word_timestamps"] = timestamps
    media_assets["subtitle_path"] = "mock://subtitles/output.srt"
    return add_log(state, f"subtitle_generator: generated {len(timestamps)} subtitle segment(s)")

