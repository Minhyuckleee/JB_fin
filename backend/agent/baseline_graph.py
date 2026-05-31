from __future__ import annotations

import re
from typing import Any, Literal

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


CONTENT_FORMAT = "shortform"
DEFAULT_TARGET = "입국 초기 외국인 유학생"
DEFAULT_LANGUAGE = "쉬운 한국어 + 영어"
DEFAULT_LENGTH = "15초"
DEFAULT_TONE = "쉽고 신뢰감 있는 톤"
MAX_REVISIONS = 2

PROHIBITED_TERMS = ["무조건", "누구나", "100% 승인", "즉시 확정", "최고 혜택 보장"]


########### State ###########
# LangGraph가 단계마다 들고 다니는 작업 노트입니다.
class BaselineState(TypedDict, total=False):
    query: str
    cleaned_request: dict[str, Any]
    missing_required_info: list[dict[str, str]]
    clarification_questions: list[str]
    content_format: str
    jb_content_type: Literal[
        "product_promotion",
        "product_guide",
        "financial_education",
        "event_campaign",
        "branch_app_guide",
    ]
    target_profile: dict[str, Any]
    language_plan: dict[str, Any]
    rag_queries: list[str]
    retrieved_context: list[dict[str, Any]]
    verified_facts: dict[str, Any]
    preflight_risk_report: dict[str, Any]
    creative_plan: dict[str, Any]
    script: dict[str, Any]
    easy_language_script: dict[str, Any]
    captions: list[dict[str, str]]
    hashtags: list[str]
    compliance_report: dict[str, Any]
    approval_request: dict[str, Any]
    employee_review: dict[str, Any]
    revision_target: str
    final_package: dict[str, Any]
    status: Literal[
        "normalized",
        "waiting_for_info",
        "required_info_ready",
        "content_type_classified",
        "target_language_set",
        "rag_queries_built",
        "context_retrieved",
        "facts_extracted",
        "blocked_by_preflight_risk",
        "preflight_passed",
        "creative_planned",
        "script_generated",
        "easy_language_ready",
        "captions_ready",
        "compliance_passed",
        "compliance_needs_revision",
        "waiting_for_approval",
        "approved",
        "revision_requested",
        "revision_in_progress",
        "revision_limit_reached",
        "completed_mock",
    ]
    logs: list[str]
    revision_count: int


def with_log(state: BaselineState, message: str) -> list[str]:
    return [*state.get("logs", []), message]


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def detect_product_name(query: str) -> str | None:
    explicit = re.search(r"(?:상품명|상품)\s*[:=]\s*([^,\n]+)", query)
    if explicit:
        return normalize_text(explicit.group(1))

    branded = re.search(
        r"((?:JB|전북은행)\s*[A-Za-z0-9가-힣\s]*?"
        r"(?:체크카드|신용카드|카드|대출|예금|적금|통장|계좌|금융상품))",
        query,
    )
    if branded:
        return normalize_text(branded.group(1))

    return None


def detect_topic(query: str) -> str | None:
    topic_patterns = [
        (r"보이스피싱|피싱|사기", "보이스피싱 주의사항"),
        (r"계좌\s*확인", "JB 앱 계좌 확인 방법"),
        (r"앱.*(?:사용|이용|확인)", "JB 앱 이용 안내"),
        (r"영업점|지점", "영업점 이용 안내"),
        (r"환전|외화|환율", "외화/환전 안내"),
    ]
    for pattern, topic in topic_patterns:
        if re.search(pattern, query):
            return topic
    return None


def detect_target(query: str) -> str:
    if "유학생" in query:
        return "외국인 유학생"
    if "외국인 고객" in query:
        return "외국인 고객"
    if "외국인 근로자" in query or "근로자" in query:
        return "외국인 근로자"
    return DEFAULT_TARGET


def detect_language(query: str) -> str:
    language_keywords = {
        "영어": "영어",
        "베트남어": "베트남어",
        "중국어": "중국어",
        "태국어": "태국어",
        "인도네시아어": "인도네시아어",
    }
    for keyword, language in language_keywords.items():
        if keyword in query:
            return language
    return DEFAULT_LANGUAGE


def detect_length(query: str) -> str:
    seconds = re.search(r"(\d+)\s*초", query)
    if seconds:
        return f"{seconds.group(1)}초"
    return DEFAULT_LENGTH


def detect_purpose(query: str) -> str | None:
    if "홍보" in query or "추천" in query:
        return "홍보"
    if "안내" in query or "알려" in query or "방법" in query:
        return "안내"
    if "주의" in query or "교육" in query:
        return "교육"
    return None


def has_shortform_output(query: str) -> bool:
    return any(keyword in query for keyword in ["숏폼", "영상", "릴스", "쇼츠", "short"])


def build_citation_ids(context: list[dict[str, Any]]) -> list[str]:
    return [item["citation_id"] for item in context if item.get("citation_id")]


##############################
# 1. 입력 정리
##############################


########### 직원 입력 정리 ###########
def normalize_employee_input(state: BaselineState) -> dict[str, Any]:
    query = normalize_text(state.get("query", ""))
    product_name = detect_product_name(query)
    topic = detect_topic(query)
    purpose = detect_purpose(query)

    cleaned_request = {
        "raw_query": state.get("query", ""),
        "normalized_query": query,
        "product_name": product_name,
        "topic": topic,
        "subject": product_name or topic,
        "purpose": purpose,
        "requested_output": "shortform" if has_shortform_output(query) else None,
        "target_hint": detect_target(query),
        "language_hint": detect_language(query),
        "length_hint": detect_length(query),
    }

    return {
        "query": query,
        "cleaned_request": cleaned_request,
        "missing_required_info": [],
        "clarification_questions": [],
        "content_format": "",
        "jb_content_type": "",
        "target_profile": {},
        "language_plan": {},
        "rag_queries": [],
        "retrieved_context": [],
        "verified_facts": {},
        "preflight_risk_report": {},
        "creative_plan": {},
        "script": {},
        "easy_language_script": {},
        "captions": [],
        "hashtags": [],
        "compliance_report": {},
        "approval_request": {},
        "revision_target": "",
        "final_package": {},
        "revision_count": int(state.get("revision_count", 0)),
        "status": "normalized",
        "logs": ["1 입력 정리: 직원 요청을 구조화했습니다."],
    }


########### 필수 정보 부족 여부 확인 ###########
def check_required_info(state: BaselineState) -> dict[str, Any]:
    request = state.get("cleaned_request", {})
    missing: list[dict[str, str]] = []

    if not request.get("subject"):
        missing.append(
            {
                "field": "subject",
                "reason": "홍보/안내할 상품명 또는 금융 주제가 필요합니다.",
            }
        )
    if not request.get("purpose"):
        missing.append(
            {
                "field": "purpose",
                "reason": "홍보, 안내, 교육 중 어떤 목적의 콘텐츠인지 필요합니다.",
            }
        )
    if not request.get("requested_output"):
        missing.append(
            {
                "field": "requested_output",
                "reason": "이번 베이스라인은 숏폼 요청을 기준으로 실행합니다.",
            }
        )

    if missing:
        questions = [
            "어떤 상품 또는 금융 주제를 다룰까요? 예: JB 유학생 체크카드, 보이스피싱 주의사항",
            "콘텐츠 목적은 홍보, 안내, 교육 중 무엇인가요?",
            "숏폼 영상으로 제작하는 요청이 맞나요?",
        ]
        return {
            "missing_required_info": missing,
            "clarification_questions": questions,
            "status": "waiting_for_info",
            "logs": with_log(state, "2 필수 정보 확인: 부족한 정보가 있어 멈췄습니다."),
        }

    return {
        "missing_required_info": [],
        "clarification_questions": [],
        "status": "required_info_ready",
        "logs": with_log(state, "2 필수 정보 확인: 진행 가능한 요청입니다."),
    }


def route_after_required_info(state: BaselineState) -> str:
    if state.get("status") == "waiting_for_info":
        return "wait"
    return "continue"


##############################
# 2. 방향 설정
##############################


########### 콘텐츠 유형 분류 ###########
def classify_content_type(state: BaselineState) -> dict[str, Any]:
    query = state.get("query", "")

    if any(keyword in query for keyword in ["이벤트", "캠페인", "행사"]):
        jb_content_type = "event_campaign"
    elif any(keyword in query for keyword in ["앱", "영업점", "지점", "계좌 확인"]):
        jb_content_type = "branch_app_guide"
    elif any(keyword in query for keyword in ["보이스피싱", "피싱", "사기", "주의", "교육"]):
        jb_content_type = "financial_education"
    elif any(keyword in query for keyword in ["가입", "발급", "사용", "방법", "안내"]):
        jb_content_type = "product_guide"
    else:
        jb_content_type = "product_promotion"

    return {
        "content_format": CONTENT_FORMAT,
        "jb_content_type": jb_content_type,
        "status": "content_type_classified",
        "logs": with_log(
            state,
            f"3 콘텐츠 유형 분류: 숏폼 안에서 {jb_content_type} 유형으로 분류했습니다.",
        ),
    }


########### 외국인 타깃과 언어 설정 ###########
def set_target_and_language(state: BaselineState) -> dict[str, Any]:
    request = state.get("cleaned_request", {})
    target = request.get("target_hint") or DEFAULT_TARGET
    language = request.get("language_hint") or DEFAULT_LANGUAGE

    target_profile = {
        "primary_target": target,
        "assumed_context": "한국 금융 서비스 이용 경험이 많지 않은 외국인 소비자",
        "pain_points": [
            "금융 용어가 어렵다",
            "공식 정보와 광고성 정보를 구분하기 어렵다",
            "앱/영업점 이용 절차가 낯설다",
        ],
    }
    language_plan = {
        "primary_language": language,
        "style": "짧은 문장, 쉬운 단어, 과장 없는 표현",
        "length": request.get("length_hint") or DEFAULT_LENGTH,
        "tone": DEFAULT_TONE,
    }

    return {
        "target_profile": target_profile,
        "language_plan": language_plan,
        "status": "target_language_set",
        "logs": with_log(state, "4 방향 설정: 외국인 타깃과 언어 기준을 정했습니다."),
    }


##############################
# 3. 근거 확보 (RAG)
##############################


########### JB 문서/FAQ/상품 정보 검색 쿼리 생성 ###########
def build_rag_queries(state: BaselineState) -> dict[str, Any]:
    request = state.get("cleaned_request", {})
    subject = request.get("subject", "JB 금융 콘텐츠")
    jb_content_type = state.get("jb_content_type", "product_promotion")

    rag_queries = [
        f"{subject} 공식 상품 정보",
        f"{subject} 외국인 고객 FAQ",
        f"{subject} 광고 준법 유의사항",
        f"JB {jb_content_type} 숏폼 콘텐츠 근거",
    ]

    return {
        "rag_queries": rag_queries,
        "status": "rag_queries_built",
        "logs": with_log(state, "5 RAG 쿼리 생성: 검색할 질문을 만들었습니다."),
    }


########### JB 문서/FAQ/상품 정보 검색 ###########
def retrieve_jb_context(state: BaselineState) -> dict[str, Any]:
    request = state.get("cleaned_request", {})
    subject = request.get("subject", "JB 금융 콘텐츠")
    jb_content_type = state.get("jb_content_type", "product_promotion")

    common_context = [
        {
            "citation_id": "jb_rule_001",
            "source": "JB mock compliance guide",
            "text": "금융 콘텐츠는 상품 조건을 확정적으로 표현하지 않고 공식 채널 확인을 안내해야 합니다.",
        },
        {
            "citation_id": "jb_foreign_001",
            "source": "JB mock foreign customer FAQ",
            "text": "외국인 고객 안내 문구는 짧고 쉬운 문장으로 작성하며 어려운 금융 용어는 풀어서 설명합니다.",
        },
    ]

    type_context = {
        "product_promotion": {
            "citation_id": "jb_product_001",
            "source": "JB mock product document",
            "text": f"{subject} 홍보 시 혜택은 공식 상품 설명서 기준으로 안내해야 합니다.",
        },
        "product_guide": {
            "citation_id": "jb_guide_001",
            "source": "JB mock product FAQ",
            "text": f"{subject} 안내 콘텐츠는 준비물, 이용 절차, 공식 확인 경로를 순서대로 설명합니다.",
        },
        "financial_education": {
            "citation_id": "jb_education_001",
            "source": "JB mock financial education FAQ",
            "text": "보이스피싱 등 금융사기 예방 콘텐츠는 의심 상황, 확인 방법, 공식 신고 경로를 안내합니다.",
        },
        "event_campaign": {
            "citation_id": "jb_event_001",
            "source": "JB mock event notice",
            "text": "이벤트 콘텐츠는 기간, 대상, 조건, 유의사항을 명확히 함께 안내해야 합니다.",
        },
        "branch_app_guide": {
            "citation_id": "jb_app_001",
            "source": "JB mock app guide",
            "text": "앱/영업점 안내 콘텐츠는 고객이 따라 할 수 있는 단계와 공식 확인 경로를 제공합니다.",
        },
    }

    retrieved_context = [type_context[jb_content_type], *common_context]
    return {
        "retrieved_context": retrieved_context,
        "status": "context_retrieved",
        "logs": with_log(state, "6 RAG 검색: mock JB 자료를 검색했습니다."),
    }


########### 검색 자료에서 검증된 fact 추출 ###########
def extract_verified_facts(state: BaselineState) -> dict[str, Any]:
    request = state.get("cleaned_request", {})
    context = state.get("retrieved_context", [])
    citation_ids = build_citation_ids(context)

    verified_facts = {
        "subject": request.get("subject"),
        "product_name": request.get("product_name"),
        "topic": request.get("topic"),
        "jb_content_type": state.get("jb_content_type"),
        "facts": [
            "공식 채널에서 조건과 세부 내용을 확인하도록 안내해야 합니다.",
            "외국인 소비자에게는 짧고 쉬운 표현을 사용해야 합니다.",
            "확정적 혜택, 무조건 승인, 최고 혜택 보장 표현은 피해야 합니다.",
        ],
        "required_disclaimer": "상품 조건과 혜택은 공식 안내 및 내부 기준에 따라 달라질 수 있습니다.",
        "prohibited_terms": PROHIBITED_TERMS,
        "citation_ids": citation_ids,
    }

    return {
        "verified_facts": verified_facts,
        "status": "facts_extracted",
        "logs": with_log(state, "7 fact 추출: 검색 자료에서 검증된 fact만 정리했습니다."),
    }


########### 제작 전 위험도 사전 점검 ###########
def preflight_risk_check(state: BaselineState) -> dict[str, Any]:
    query = state.get("query", "")
    facts = state.get("verified_facts", {})
    blocking_issues = []

    if not facts.get("citation_ids"):
        blocking_issues.append("근거 citation이 없습니다.")
    for term in PROHIBITED_TERMS:
        if term in query:
            blocking_issues.append(f"직원 요청에 위험 표현({term})이 포함되어 있습니다.")

    report = {
        "risk_level": "blocking" if blocking_issues else "low",
        "blocking_issues": blocking_issues,
        "checks": ["citation_exists", "prohibited_terms_in_request", "official_channel_required"],
    }

    return {
        "preflight_risk_report": report,
        "status": "blocked_by_preflight_risk" if blocking_issues else "preflight_passed",
        "logs": with_log(
            state,
            "8 사전 점검: 차단 위험이 있습니다." if blocking_issues else "8 사전 점검: 제작 가능 상태입니다.",
        ),
    }


def route_after_preflight(state: BaselineState) -> str:
    if state.get("status") == "blocked_by_preflight_risk":
        return "blocked"
    return "continue"


##############################
# 4. 콘텐츠 생성 (Tool API)
##############################


########### 훅, 흐름, CTA 기획 ###########
def plan_hook_flow_cta(state: BaselineState) -> dict[str, Any]:
    facts = state.get("verified_facts", {})
    jb_content_type = state.get("jb_content_type", "product_promotion")
    subject = facts.get("subject", "JB 금융 콘텐츠")

    hooks = {
        "product_promotion": f"{subject}, 처음이라도 쉽게 확인할 수 있어요.",
        "product_guide": f"{subject}, 순서만 알면 어렵지 않아요.",
        "financial_education": "낯선 금융 연락, 바로 믿기 전에 확인하세요.",
        "event_campaign": f"{subject} 이벤트 조건을 먼저 확인하세요.",
        "branch_app_guide": "JB 앱과 영업점 이용, 이렇게 확인하세요.",
    }

    creative_plan = {
        "hook": hooks[jb_content_type],
        "flow": ["공감 상황 제시", "공식 정보 확인", "쉬운 행동 안내"],
        "cta": "JB 공식 앱 또는 영업점에서 확인하기",
        "message_guardrail": "혜택을 확정하지 않고 공식 확인 행동을 유도합니다.",
    }

    return {
        "creative_plan": creative_plan,
        "status": "creative_planned",
        "logs": with_log(state, "9 기획: 훅, 흐름, CTA를 정했습니다."),
    }


########### 숏폼 대본 생성 ###########
def generate_shortform_script(state: BaselineState) -> dict[str, Any]:
    facts = state.get("verified_facts", {})
    plan = state.get("creative_plan", {})
    language = state.get("language_plan", {})
    citation_ids = facts.get("citation_ids", [])
    revision_count = int(state.get("revision_count", 0))

    hook = plan.get("hook", "JB 금융 정보를 쉽게 확인하세요.")
    if revision_count:
        hook = f"잠깐, {hook}"

    script = {
        "format": CONTENT_FORMAT,
        "estimated_length": language.get("length", DEFAULT_LENGTH),
        "lines": [
            {"line_id": "line_1", "text": hook, "citation_ids": citation_ids},
            {
                "line_id": "line_2",
                "text": "조건과 세부 내용은 공식 안내에서 확인하는 것이 가장 안전합니다.",
                "citation_ids": citation_ids,
            },
            {
                "line_id": "line_3",
                "text": "JB 공식 앱 또는 영업점에서 나에게 맞는 정보를 확인해보세요.",
                "citation_ids": citation_ids,
            },
        ],
    }

    return {
        "script": script,
        "status": "script_generated",
        "logs": with_log(state, "10 대본 생성: 숏폼 대본을 만들었습니다."),
    }


########### 외국인 소비자용 쉬운 표현 변환 ###########
def simplify_for_foreign_consumer(state: BaselineState) -> dict[str, Any]:
    script = state.get("script", {})
    simple_lines = []
    for line in script.get("lines", []):
        text = line.get("text", "")
        text = text.replace("세부 내용", "자세한 내용")
        text = text.replace("확인하는 것이 가장 안전합니다", "확인하면 안전합니다")
        simple_lines.append({**line, "text": text})

    easy_language_script = {
        "format": script.get("format", CONTENT_FORMAT),
        "estimated_length": script.get("estimated_length", DEFAULT_LENGTH),
        "lines": simple_lines,
        "style_note": "외국인 소비자가 이해하기 쉽게 짧은 문장으로 정리했습니다.",
    }

    return {
        "easy_language_script": easy_language_script,
        "status": "easy_language_ready",
        "logs": with_log(state, "11 쉬운 표현 변환: 외국인 소비자용 문장으로 바꿨습니다."),
    }


########### 자막, 캡션, 해시태그 생성 ###########
def generate_captions_and_hashtags(state: BaselineState) -> dict[str, Any]:
    easy_script = state.get("easy_language_script", {})
    lines = easy_script.get("lines", [])
    captions = [
        {"caption_id": line.get("line_id", f"caption_{index}"), "text": line.get("text", "")}
        for index, line in enumerate(lines, start=1)
    ]
    hashtags = ["#JB금융", "#외국인금융", "#쉬운금융", "#공식채널확인"]

    return {
        "captions": captions,
        "hashtags": hashtags,
        "status": "captions_ready",
        "logs": with_log(state, "12 자막/캡션/해시태그: 배포용 텍스트를 만들었습니다."),
    }


##############################
# 5. 검수 및 출력
##############################


########### 최종 문구 준법 검토 ###########
def final_compliance_check(state: BaselineState) -> dict[str, Any]:
    facts = state.get("verified_facts", {})
    lines = state.get("easy_language_script", {}).get("lines", [])
    captions = state.get("captions", [])
    full_text = " ".join(
        [line.get("text", "") for line in lines] + [caption.get("text", "") for caption in captions]
    )

    issues = []
    for term in facts.get("prohibited_terms", PROHIBITED_TERMS):
        if term in full_text:
            issues.append(
                {
                    "type": "prohibited_term",
                    "text": term,
                    "reason": "금융 광고에서 소비자를 오인시킬 수 있는 표현입니다.",
                }
            )
    for line in lines:
        if not line.get("citation_ids"):
            issues.append(
                {
                    "type": "missing_citation",
                    "text": line.get("line_id", "unknown"),
                    "reason": "생성 문구에 근거 citation이 없습니다.",
                }
            )

    report_status = "needs_revision" if issues else "approved"
    return {
        "compliance_report": {
            "status": report_status,
            "issues": issues,
            "checked_items": ["prohibited_terms", "citation_links", "official_channel_cta"],
        },
        "status": "compliance_needs_revision" if issues else "compliance_passed",
        "logs": with_log(state, f"13 준법 검토: {report_status} 상태입니다."),
    }


########### 직원 승인/수정 요청 ###########
def request_employee_approval(state: BaselineState) -> dict[str, Any]:
    review = state.get("employee_review", {})
    decision = review.get("decision")
    revision_count = int(state.get("revision_count", 0))
    approval_request = {
        "message": "직원이 최종 문구를 승인하거나 수정 요청을 남길 차례입니다.",
        "allowed_decisions": ["approved", "revise"],
        "summary": {
            "content_format": state.get("content_format"),
            "jb_content_type": state.get("jb_content_type"),
            "compliance_status": state.get("compliance_report", {}).get("status"),
        },
    }

    if decision == "approved":
        return {
            "approval_request": approval_request,
            "status": "approved",
            "logs": with_log(state, "14 직원 승인: 승인되어 최종 패키지로 이동합니다."),
        }

    if decision == "revise":
        if revision_count >= MAX_REVISIONS:
            return {
                "approval_request": approval_request,
                "status": "revision_limit_reached",
                "logs": with_log(state, "14 직원 승인: 최대 수정 횟수에 도달해 멈췄습니다."),
            }

        issue_type = review.get("issue_type", "unknown")
        revision_target = {
            "missing_context": "retrieve_jb_context",
            "wrong_fact": "extract_verified_facts",
            "risky_direction": "plan_hook_flow_cta",
            "bad_script": "generate_shortform_script",
            "hard_expression": "simplify_for_foreign_consumer",
            "bad_caption": "generate_captions_and_hashtags",
            "compliance_issue": "generate_shortform_script",
            "unknown": "plan_hook_flow_cta",
        }.get(issue_type, "plan_hook_flow_cta")

        return {
            "approval_request": approval_request,
            "revision_target": revision_target,
            "revision_count": revision_count + 1,
            "status": "revision_requested",
            "logs": with_log(
                state,
                f"14 직원 승인: 수정 요청({issue_type})으로 {revision_target} 단계로 되돌립니다.",
            ),
        }

    return {
        "approval_request": approval_request,
        "status": "waiting_for_approval",
        "logs": with_log(state, "14 직원 승인: 승인 또는 수정 요청을 기다립니다."),
    }


def route_after_employee_approval(state: BaselineState) -> str:
    if state.get("status") == "approved":
        return "final"
    if state.get("status") == "revision_requested":
        return "revise"
    return "end"


########### 수정 요청 라우터 ###########
def revision_router(state: BaselineState) -> dict[str, Any]:
    return {
        "employee_review": {},
        "status": "revision_in_progress",
        "logs": with_log(state, "15 수정 라우터: 수정 요청을 반영할 단계로 이동합니다."),
    }


def route_revision_target(state: BaselineState) -> str:
    return state.get("revision_target", "plan_hook_flow_cta")


########### 최종 콘텐츠 패키지 생성 ###########
def final_content_package(state: BaselineState) -> dict[str, Any]:
    final_package = {
        "content_format": state.get("content_format"),
        "jb_content_type": state.get("jb_content_type"),
        "target_profile": state.get("target_profile"),
        "language_plan": state.get("language_plan"),
        "verified_facts": state.get("verified_facts"),
        "creative_plan": state.get("creative_plan"),
        "script": state.get("easy_language_script"),
        "captions": state.get("captions"),
        "hashtags": state.get("hashtags"),
        "compliance_report": state.get("compliance_report"),
        "citations": state.get("retrieved_context"),
        "rendering_note": "실제 영상 생성 API는 다음 구현 단계에서 연결합니다.",
    }

    return {
        "final_package": final_package,
        "status": "completed_mock",
        "logs": with_log(state, "16 최종 패키지: mock 콘텐츠 패키지를 생성했습니다."),
    }


##############################
# 그래프 조립
##############################

builder = StateGraph(BaselineState)

builder.add_node("normalize_employee_input", normalize_employee_input)
builder.add_node("check_required_info", check_required_info)
builder.add_node("classify_content_type", classify_content_type)
builder.add_node("set_target_and_language", set_target_and_language)
builder.add_node("build_rag_queries", build_rag_queries)
builder.add_node("retrieve_jb_context", retrieve_jb_context)
builder.add_node("extract_verified_facts", extract_verified_facts)
builder.add_node("preflight_risk_check", preflight_risk_check)
builder.add_node("plan_hook_flow_cta", plan_hook_flow_cta)
builder.add_node("generate_shortform_script", generate_shortform_script)
builder.add_node("simplify_for_foreign_consumer", simplify_for_foreign_consumer)
builder.add_node("generate_captions_and_hashtags", generate_captions_and_hashtags)
builder.add_node("final_compliance_check", final_compliance_check)
builder.add_node("request_employee_approval", request_employee_approval)
builder.add_node("revision_router", revision_router)
builder.add_node("final_content_package", final_content_package)

builder.add_edge(START, "normalize_employee_input")
builder.add_edge("normalize_employee_input", "check_required_info")

builder.add_conditional_edges(
    "check_required_info",
    route_after_required_info,
    {
        "wait": END,
        "continue": "classify_content_type",
    },
)

builder.add_edge("classify_content_type", "set_target_and_language")
builder.add_edge("set_target_and_language", "build_rag_queries")
builder.add_edge("build_rag_queries", "retrieve_jb_context")
builder.add_edge("retrieve_jb_context", "extract_verified_facts")
builder.add_edge("extract_verified_facts", "preflight_risk_check")

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
builder.add_edge("generate_captions_and_hashtags", "final_compliance_check")
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

builder.add_conditional_edges(
    "revision_router",
    route_revision_target,
    {
        "retrieve_jb_context": "retrieve_jb_context",
        "extract_verified_facts": "extract_verified_facts",
        "plan_hook_flow_cta": "plan_hook_flow_cta",
        "generate_shortform_script": "generate_shortform_script",
        "simplify_for_foreign_consumer": "simplify_for_foreign_consumer",
        "generate_captions_and_hashtags": "generate_captions_and_hashtags",
    },
)

builder.add_edge("final_content_package", END)

graph = builder.compile()
