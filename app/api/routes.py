"""FastAPI route definitions for AskPodcast."""
import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agent.graph import corrective_rag_agent
from app.schemas import AskRequest, AskResponse, Citation

router = APIRouter()


def _build_citations(documents: list) -> list[Citation]:
    """Build structured, clickable YouTube citation models from document metadata."""
    citations: list[Citation] = []
    seen = set()

    for doc in documents:
        meta = doc.metadata
        chunk_id = meta.get("chunk_id", "")
        if chunk_id in seen:
            continue
        seen.add(chunk_id)

        start_sec = int(meta.get("start_seconds", 0))
        ep_id = meta.get("episode_id", "")
        deep_link = f"https://youtu.be/{ep_id}?t={start_sec}" if ep_id else ""

        citations.append(
            Citation(
                episode_title=meta.get("episode_title", "Unknown Episode"),
                episode_id=ep_id,
                speaker=meta.get("speaker", "Speaker"),
                timestamp=meta.get("timestamp", "00:00:00"),
                start_seconds=meta.get("start_seconds", 0.0),
                url=deep_link,
            )
        )
    return citations


@router.get("/health")
def health_check() -> dict[str, str]:
    """Health check probe for container readiness."""
    return {"status": "ok", "app": "AskPodcast"}


@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest) -> AskResponse:
    """Submit a question and receive a complete answer with clickable timestamp citations."""
    try:
        initial_state = {
            "question": request.question,
            "documents": [],
            "relevant_documents": [],
            "rewrite_count": 0,
            "generation": "",
        }

        final_state = corrective_rag_agent.invoke(initial_state)
        relevant_docs = final_state.get("relevant_documents", [])
        citations = _build_citations(relevant_docs)

        return AskResponse(
            question=request.question,
            answer=final_state.get("generation", ""),
            citations=citations,
            rewrites_attempted=final_state.get("rewrite_count", 0),
            relevant_chunks_used=len(relevant_docs),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")


@router.post("/ask/stream")
async def stream_question(request: AskRequest) -> StreamingResponse:
    """Stream LangGraph node events and final answer in real-time via Server-Sent Events."""
    async def event_generator() -> AsyncGenerator[str, None]:
        initial_state = {
            "question": request.question,
            "documents": [],
            "relevant_documents": [],
            "rewrite_count": 0,
            "generation": "",
        }

        for event in corrective_rag_agent.stream(initial_state):
            for node_name, node_output in event.items():
                event_data = {
                    "node": node_name,
                    "rewrites": node_output.get("rewrite_count", 0),
                }
                if node_name == "retrieve":
                    event_data["chunks_retrieved"] = len(node_output.get("documents", []))
                elif node_name == "grade_documents":
                    rel = node_output.get("relevant_documents", [])
                    event_data["relevant_chunks"] = len(rel)
                    event_data["citations"] = [c.model_dump() for c in _build_citations(rel)]
                elif node_name == "rewrite_query":
                    event_data["rewritten_query"] = node_output.get("question", "")
                elif node_name == "generate":
                    event_data["generation"] = node_output.get("generation", "")

                yield f"data: {json.dumps(event_data)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
