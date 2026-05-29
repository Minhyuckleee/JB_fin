import os
from typing import Literal

from typing_extensions import TypedDict

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph


########### 실행 흐름 ###########
# START -> classify_question -> 조건 분기 -> 각 답변 노드 -> END
# exchange 분기는 LLM이 도구를 고른 뒤, 도구 결과로 답변을 만듭니다.


##############################
# 1. 재료 준비
# - State 정의
# - Node 함수 정의
# - Router 함수 정의
##############################


########### State ###########
# 그래프가 들고 다니는 데이터입니다.
class StudyState(TypedDict, total=False):
    question: str
    category: Literal["loan", "card", "exchange", "general"]
    reason: str
    tool_name: str
    tool_result: str
    answer: str


########### Node: 질문 분류 ###########
# question을 읽고 category와 reason을 채웁니다.
# 원래는 이것도 LLM으로 분류 함. 
def classify_question(state: StudyState) -> dict[str, str]:
    question = state.get("question", "")
    keyword_groups = {
        "loan": ["대출", "금리", "상환"],
        "card": ["카드", "체크카드", "신용카드"],
        "exchange": ["환율", "환전", "외화"],
    }

    for category, keywords in keyword_groups.items():
        matched_keywords = [keyword for keyword in keywords if keyword in question]
        if matched_keywords:
            return {
                "category": category,
                "reason": f"{category} 키워드({', '.join(matched_keywords)})가 포함되어 있습니다.",
            }

    return {
        "category": "general",
        "reason": "금융 세부 키워드가 없어 일반 질문으로 분류했습니다.", # 판단 근거
    }


########### Router: 분기 선택 ###########
# category 값으로 다음 노드를 고릅니다.
def choose_answer_node(state: StudyState) -> str:
    return state.get("category", "general")


########### Node: 대출 답변 ###########
def answer_loan_question(state: StudyState) -> dict[str, str]:
    return {
        "answer": "대출 질문입니다. 실제 서비스라면 여기서 대출 상담 노드가 실행됩니다."
    }


########### Node: 카드 답변 ###########
def answer_card_question(state: StudyState) -> dict[str, str]:
    return {
        "answer": "카드 질문입니다. 실제 서비스라면 여기서 카드 안내 노드가 실행됩니다."
    }


########### Tool: 환율 조회 ###########
# 실제 API 대신 고정된 예시 데이터를 반환합니다.
@tool
def get_usd_krw_exchange_rate() -> str:
    """현재 USD/KRW 환율 예시 데이터를 조회합니다."""
    return "1 USD = 1,380 KRW"


########### Node: LLM 도구 선택 ###########
# 여기서 "원화 환율 알려줘" 라고 질문을 다시 보여줌.
def choose_exchange_tool_with_llm(state: StudyState) -> dict[str, str]:
    if not os.getenv("OPENAI_API_KEY"):
        return {
            "tool_name": "get_usd_krw_exchange_rate",
            "reason": "OPENAI_API_KEY가 없어 학습용으로 환율 도구 선택을 가정했습니다.",
        }

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-5.4-nano"),
        temperature=0,
    ).bind_tools([get_usd_krw_exchange_rate]) # 환율 api tool

    response = llm.invoke(
        [
            (
                "system",
                "환율 정보가 필요한 질문이면 get_usd_krw_exchange_rate 도구를 호출하세요.",
            ),
            ("human", state.get("question", "")),
        ]
    )

    if response.tool_calls:
        return {
            "tool_name": response.tool_calls[0]["name"],
            "reason": "LLM이 환율 도구가 필요하다고 판단했습니다.",
        }

    return {
        "tool_name": "",
        "reason": "LLM이 도구 없이 답변할 수 있다고 판단했습니다.",
    }


########### Node: 선택된 도구 실행 ###########
def run_selected_exchange_tool(state: StudyState) -> dict[str, str]:
    if state.get("tool_name") == "get_usd_krw_exchange_rate":
        return {"tool_result": get_usd_krw_exchange_rate.invoke({})}

    return {"tool_result": "사용할 도구가 선택되지 않았습니다."}


########### LLM: 환율 답변 생성 ###########
def generate_exchange_answer_with_llm(question: str, exchange_rate: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        return f"OPENAI_API_KEY가 없어 LLM 답변 생성을 건너뛰었습니다. 도구 결과: {exchange_rate}"

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-5.4-nano"),
        temperature=0,
    )
    response = llm.invoke(
        [
            (
                "system",
                "주어진 환율 정보만 사용해서 사용자의 질문에 한국어로 짧게 답변하세요.",
            ),
            ("human", f"질문: {question}\n환율 정보: {exchange_rate}"),
        ]
    )
    return str(response.content)


########### Node: 환율 답변 ###########
def answer_exchange_question(state: StudyState) -> dict[str, str]:
    exchange_rate = state.get("tool_result", "환율 정보 없음")
    answer = generate_exchange_answer_with_llm(state.get("question", ""), exchange_rate)
    return {"answer": answer}


########### Node: 일반 답변 ###########
def answer_general_question(state: StudyState) -> dict[str, str]:
    return {
        "answer": "일반 질문입니다. 실제 서비스라면 여기서 일반 응답 노드가 실행됩니다."
    }


##############################
# 2. 그래프 조립
# - Graph 생성
# - Node 등록
# - Edge 연결
# - Compile
##############################


########### Graph 생성 ###########
builder = StateGraph(StudyState)


########### Node 등록 ###########
builder.add_node("classify_question", classify_question)
builder.add_node("answer_loan_question", answer_loan_question)
builder.add_node("answer_card_question", answer_card_question)
builder.add_node("choose_exchange_tool_with_llm", choose_exchange_tool_with_llm)
builder.add_node("run_selected_exchange_tool", run_selected_exchange_tool)
builder.add_node("answer_exchange_question", answer_exchange_question)
builder.add_node("answer_general_question", answer_general_question)


########### Edge 연결 ###########
builder.add_edge(START, "classify_question")


########### Conditional Edge 연결 ###########
builder.add_conditional_edges(
    "classify_question",
    choose_answer_node,
    {
        "loan": "answer_loan_question",
        "card": "answer_card_question",
        "exchange": "choose_exchange_tool_with_llm",
        "general": "answer_general_question",
    },
)


########### 종료 연결 ###########
builder.add_edge("answer_loan_question", END)
builder.add_edge("answer_card_question", END)
builder.add_edge("choose_exchange_tool_with_llm", "run_selected_exchange_tool")
builder.add_edge("run_selected_exchange_tool", "answer_exchange_question")
builder.add_edge("answer_general_question", END)
builder.add_edge("answer_exchange_question", END)


########### Compile ###########
graph = builder.compile()
