from __future__ import annotations

from backend.agent.state import CampaignState, add_log


def render_video(state: CampaignState) -> CampaignState:
    """Mock video assembly.

    Replace this with Remotion + FFmpeg rendering.
    """
    state.setdefault("media_assets", {})["video_path"] = "mock://video/final_shortform.mp4"
    return add_log(state, "video_editor: rendered mock final video")

