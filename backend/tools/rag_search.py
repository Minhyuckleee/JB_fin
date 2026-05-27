from __future__ import annotations

from backend.agent.state import CampaignState, add_log


def search_rag(state: CampaignState) -> CampaignState:
    """Mock RAG search.

    Replace this with hybrid BM25/vector search using pgvector or Chroma.
    """
    citations = []
    for chunk in state.get("parsed_documents", []):
        citations.append(
            {
                "citation_id": f"{chunk['document_id']}_p{chunk['page']}",
                "source": chunk["source"],
                "page": chunk["page"],
                "text": chunk["text"],
                "score": 0.91,
            }
        )

    state["rag_citations"] = citations
    return add_log(state, f"rag_search: found {len(citations)} citation(s)")

