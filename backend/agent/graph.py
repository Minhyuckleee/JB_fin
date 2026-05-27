from __future__ import annotations

import json
from collections.abc import Callable

from backend.agent.state import CampaignState, create_initial_state
from backend.tools.compliance_checker import check_compliance
from backend.tools.document_parser import parse_documents
from backend.tools.image_generator import generate_images
from backend.tools.rag_search import search_rag
from backend.tools.script_generator import generate_script
from backend.tools.subtitle_generator import generate_subtitles
from backend.tools.target_matching import match_target
from backend.tools.translator import translate_script
from backend.tools.tts import generate_tts
from backend.tools.video_editor import render_video


Node = Callable[[CampaignState], CampaignState]


def check_script_compliance(state: CampaignState) -> CampaignState:
    return check_compliance(state, stage="korean_script")


def check_translation_compliance(state: CampaignState) -> CampaignState:
    return check_compliance(state, stage="translated_script")


PIPELINE: list[Node] = [
    match_target,
    parse_documents,
    search_rag,
    generate_script,
    check_script_compliance,
    translate_script,
    check_translation_compliance,
    generate_tts,
    generate_images,
    generate_subtitles,
    render_video,
]


def run_pipeline(initial_state: CampaignState | None = None) -> CampaignState:
    """Run the mock single-agent pipeline.

    This intentionally avoids a LangGraph dependency for now. When the team is
    ready, each function in `PIPELINE` can become a LangGraph node.
    """
    state = initial_state or create_initial_state()
    for node in PIPELINE:
        state = node(state)
    return state


if __name__ == "__main__":
    final_state = run_pipeline()
    print(json.dumps(final_state, ensure_ascii=False, indent=2))

