from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from backend.agent.baseline_graph import (
    BaselineState,
    build_rag_queries,
    check_required_info,
    classify_content_type,
    extract_verified_facts,
    final_compliance_check,
    final_content_package,
    generate_captions_and_hashtags,
    generate_shortform_script,
    normalize_employee_input,
    plan_hook_flow_cta,
    preflight_risk_check,
    request_employee_approval,
    retrieve_jb_context,
    revision_router,
    route_after_employee_approval,
    route_after_preflight,
    route_after_required_info,
    set_target_and_language,
    simplify_for_foreign_consumer,
)


########### 1. 입력 정리 Subgraph ###########
def build_input_cleanup_graph():
    builder = StateGraph(BaselineState)
    builder.add_node("normalize_employee_input", normalize_employee_input)
    builder.add_node("check_required_info", check_required_info)
    builder.add_edge(START, "normalize_employee_input")
    builder.add_edge("normalize_employee_input", "check_required_info")
    builder.add_edge("check_required_info", END)
    return builder.compile()


########### 2. 방향 설정 Subgraph ###########
def build_direction_setting_graph():
    builder = StateGraph(BaselineState)
    builder.add_node("classify_content_type", classify_content_type)
    builder.add_node("set_target_and_language", set_target_and_language)
    builder.add_edge(START, "classify_content_type")
    builder.add_edge("classify_content_type", "set_target_and_language")
    builder.add_edge("set_target_and_language", END)
    return builder.compile()


########### 3. 근거 확보 Subgraph ###########
def build_rag_grounding_graph():
    builder = StateGraph(BaselineState)
    builder.add_node("build_rag_queries", build_rag_queries)
    builder.add_node("retrieve_jb_context", retrieve_jb_context)
    builder.add_node("extract_verified_facts", extract_verified_facts)
    builder.add_edge(START, "build_rag_queries")
    builder.add_edge("build_rag_queries", "retrieve_jb_context")
    builder.add_edge("retrieve_jb_context", "extract_verified_facts")
    builder.add_edge("extract_verified_facts", END)
    return builder.compile()


########### 4. 콘텐츠 생성 Subgraph ###########
def build_content_generation_graph():
    builder = StateGraph(BaselineState)
    builder.add_node("preflight_risk_check", preflight_risk_check)
    builder.add_node("plan_hook_flow_cta", plan_hook_flow_cta)
    builder.add_node("generate_shortform_script", generate_shortform_script)
    builder.add_node("simplify_for_foreign_consumer", simplify_for_foreign_consumer)
    builder.add_node("generate_captions_and_hashtags", generate_captions_and_hashtags)

    builder.add_edge(START, "preflight_risk_check")
    builder.add_conditional_edges(
        "preflight_risk_check",
        route_after_preflight,
        {
            "blocked": END,
            "continue": "plan_hook_flow_cta",
        },
    )
    builder.add_edge("plan_hook_flow_cta", "generate_shortform_script")
    builder.add_edge("generate_shortform_script", "simplify_for_foreign_consumer")
    builder.add_edge("simplify_for_foreign_consumer", "generate_captions_and_hashtags")
    builder.add_edge("generate_captions_and_hashtags", END)
    return builder.compile()


########### 5. 검수 및 출력 Subgraph ###########
def build_review_output_graph():
    builder = StateGraph(BaselineState)
    builder.add_node("final_compliance_check", final_compliance_check)
    builder.add_node("request_employee_approval", request_employee_approval)
    builder.add_node("revision_router", revision_router)
    builder.add_node("final_content_package", final_content_package)

    builder.add_edge(START, "final_compliance_check")
    builder.add_edge("final_compliance_check", "request_employee_approval")
    builder.add_conditional_edges(
        "request_employee_approval",
        route_after_employee_approval,
        {
            "end": END,
            "final": "final_content_package",
            "revise": "revision_router",
        },
    )
    builder.add_edge("revision_router", END)
    builder.add_edge("final_content_package", END)
    return builder.compile()


def route_after_input_cleanup(state: BaselineState) -> str:
    return route_after_required_info(state)


def route_after_content_generation(state: BaselineState) -> str:
    if state.get("status") == "blocked_by_preflight_risk":
        return "end"
    return "review"


def route_after_review_output(state: BaselineState) -> str:
    if state.get("status") != "revision_in_progress":
        return "end"

    rag_targets = {"retrieve_jb_context", "extract_verified_facts"}
    if state.get("revision_target") in rag_targets:
        return "rag"
    return "content"


##############################
# 최상위 그래프
# - Studio에서는 이 5개 그룹을 중심으로 흐름을 봅니다.
##############################

input_cleanup_graph = build_input_cleanup_graph()
direction_setting_graph = build_direction_setting_graph()
rag_grounding_graph = build_rag_grounding_graph()
content_generation_graph = build_content_generation_graph()
review_output_graph = build_review_output_graph()

builder = StateGraph(BaselineState)

builder.add_node("input_cleanup", input_cleanup_graph)
builder.add_node("direction_setting", direction_setting_graph)
builder.add_node("rag_grounding", rag_grounding_graph)
builder.add_node("content_generation", content_generation_graph)
builder.add_node("review_output", review_output_graph)

builder.add_edge(START, "input_cleanup")
builder.add_conditional_edges(
    "input_cleanup",
    route_after_input_cleanup,
    {
        "wait": END,
        "continue": "direction_setting",
    },
)
builder.add_edge("direction_setting", "rag_grounding")
builder.add_edge("rag_grounding", "content_generation")
builder.add_conditional_edges(
    "content_generation",
    route_after_content_generation,
    {
        "end": END,
        "review": "review_output",
    },
)
builder.add_conditional_edges(
    "review_output",
    route_after_review_output,
    {
        "end": END,
        "rag": "rag_grounding",
        "content": "content_generation",
    },
)

graph = builder.compile()
