from __future__ import annotations

from backend.agent.state import CampaignState, add_log


def generate_images(state: CampaignState) -> CampaignState:
    """Mock image generation."""
    scenes = state.get("script_data", {}).get("scenes", [])
    image_urls = [f"mock://images/scene_{scene.get('scene_id', index)}.png" for index, scene in enumerate(scenes, start=1)]
    state.setdefault("media_assets", {})["image_urls"] = image_urls
    return add_log(state, f"image_generator: generated {len(image_urls)} mock image(s)")

