from typing import Literal

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


########### 실행 흐름 ###########
# START -> classify_question -> 조건 분기 -> answer_*_question -> END


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
    category: Literal["finance", "general"]
    answer: str


########### Node: 질문 분류 ###########
# question을 읽고 category를 채웁니다.
def classify_question(state: StudyState) -> dict[str, str]:
    question = state.get("question", "")
    finance_keywords = ["대출", "금리", "은행", "계좌", "환율", "카드"]

    if any(keyword in question for keyword in finance_keywords):
        return {"category": "finance"}

    return {"category": "general"}


########### Router: 분기 선택 ###########
# category 값으로 다음 노드를 고릅니다.
def choose_answer_node(state: StudyState) -> str:
    return state.get("category", "general")


########### Node: 금융 답변 ###########
def answer_finance_question(state: StudyState) -> dict[str, str]:
    return {
        "answer": "금융 질문입니다. 실제 서비스라면 여기서 금융 상담 노드가 실행됩니다."
    }


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
builder.add_node("answer_finance_question", answer_finance_question)
builder.add_node("answer_general_question", answer_general_question)


########### Edge 연결 ###########
builder.add_edge(START, "classify_question")


########### Conditional Edge 연결 ###########
builder.add_conditional_edges(
    "classify_question",
    choose_answer_node,
    {
        "finance": "answer_finance_question",
        "general": "answer_general_question",
    },
)


########### 종료 연결 ###########
builder.add_edge("answer_finance_question", END)
builder.add_edge("answer_general_question", END)


########### Compile ###########
graph = builder.compile()
