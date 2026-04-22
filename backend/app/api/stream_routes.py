import json
from typing import Iterator
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.app.models.chat_schemas import ChatRequest
from backend.app.core.pipeline import get_pipeline
from backend.app.core.rag_service import run_rag_stream, truncate_context

router = APIRouter()

def format_sse(event: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"

@router.post("/chat/stream")
def chat_stream(payload: ChatRequest):
    provider = payload.provider or "groq"

    def generate() -> Iterator[str]:
        try:
            #metadata event
            yield format_sse("meta", {"provider": provider})

            embedder, vector_store, llm, reranker, bm25, _ = get_pipeline(provider)

            for event, data in run_rag_stream(
                payload.query,
                embedder,
                vector_store,
                llm,
                reranker,
                bm25,
                history=[m.model_dump() for m in (payload.history or [])],
            ):
                if event == "token":
                    yield format_sse("token", data)
                elif event == "done":
                    data["context"] = truncate_context(data.get("context", ""), 600)
                    yield format_sse("done", data)
                elif event == "error":
                    yield format_sse("error", data)

        except Exception as e:
            yield format_sse("error", {"message": str(e)})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
