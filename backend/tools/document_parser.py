from __future__ import annotations

from backend.agent.state import CampaignState, add_log


def parse_documents(state: CampaignState) -> CampaignState:
    """Mock document parser.

    Replace this with PyMuPDF, LlamaParse, or Docling integration.
    """
    parsed = []
    for index, source in enumerate(state.get("raw_documents", []), start=1):
        parsed.append(
            {
                "document_id": f"doc_{index:03d}",
                "source": source,
                "page": 1,
                "section": "loan guidance",
                "text": (
                    "대출 가능 여부는 심사 결과에 따라 달라질 수 있으며, "
                    "필요 서류와 조건은 공식 채널에서 확인해야 합니다."
                ),
            }
        )

    state["parsed_documents"] = parsed
    return add_log(state, f"document_parser: parsed {len(parsed)} document(s)")

