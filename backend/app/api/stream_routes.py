import json
from typing import Iterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.app.models.schemas import ChatRequest
from backend.app.core.pipeline import get_pipeline
from backend.app.core.rag_service import run_rag_stream, truncate_context

router = APIRouter()


def sse(event: str, data: dict) -> str:
    return f"event: {event}\n" + f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/chat/stream")
def chat_stream(payload: ChatRequest):
    provider = payload.provider or "groq"

    def generate() -> Iterator[str]:
        try:
            # optional metadata event
            yield sse("meta", {"provider": provider})

            embedder, vector_store, llm, reranker, bm25, _ = get_pipeline(provider)

            for ev, data in run_rag_stream(
                payload.query,
                embedder,
                vector_store,
                llm,
                reranker,
                bm25,
                history=[m.model_dump() for m in (payload.history or [])],
            ):
                if ev == "token":
                    # expects {"delta": "..."}
                    yield sse("token", data)

                elif ev == "done":
                    # ensure context truncation in final payload
                    data["context"] = truncate_context(data.get("context", ""), 600)
                    yield sse("done", data)

                elif ev == "error":
                    # if you ever yield errors from run_rag_stream in the future
                    yield sse("error", data)

        except Exception as e:
            yield sse("error", {"message": str(e)})

    return StreamingResponse(
    generate(),
    media_type="text/event-stream",
    headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    },
)