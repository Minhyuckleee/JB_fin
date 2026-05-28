from __future__ import annotations

import json

from langgraph.graph import END, START, StateGraph

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


def check_script_compliance(state: CampaignState) -> CampaignState:
    return check_compliance(state, stage="korean_script")


def check_translation_compliance(state: CampaignState) -> CampaignState:
    return check_compliance(state, stage="translated_script")


builder = StateGraph(CampaignState)

builder.add_node("match_target", match_target)
builder.add_node("parse_documents", parse_documents)
builder.add_node("search_rag", search_rag)
builder.add_node("generate_script", generate_script)
builder.add_node("check_script_compliance", check_script_compliance)
builder.add_node("translate_script", translate_script)
builder.add_node("check_translation_compliance", check_translation_compliance)
builder.add_node("generate_tts", generate_tts)
builder.add_node("generate_images", generate_images)
builder.add_node("generate_subtitles", generate_subtitles)
builder.add_node("render_video", render_video)

builder.add_edge(START, "match_target")
builder.add_edge("match_target", "parse_documents")
builder.add_edge("parse_documents", "search_rag")
builder.add_edge("search_rag", "generate_script")
builder.add_edge("generate_script", "check_script_compliance")
builder.add_edge("check_script_compliance", "translate_script")
builder.add_edge("translate_script", "check_translation_compliance")
builder.add_edge("check_translation_compliance", "generate_tts")
builder.add_edge("generate_tts", "generate_images")
builder.add_edge("generate_images", "generate_subtitles")
builder.add_edge("generate_subtitles", "render_video")
builder.add_edge("render_video", END)

graph = builder.compile()


def run_pipeline(initial_state: CampaignState | None = None) -> CampaignState:
    """Run the mock single-agent LangGraph pipeline."""
    return graph.invoke(initial_state or create_initial_state())


if __name__ == "__main__":
    final_state = run_pipeline()
    print(json.dumps(final_state, ensure_ascii=False, indent=2))
