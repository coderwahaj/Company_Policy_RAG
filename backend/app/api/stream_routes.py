import json
from typing import Iterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.app.models.schemas import ChatRequest, ChatResponse
from backend.app.core.pipeline import get_pipeline
from backend.app.core.rag_service import run_rag, truncate_context

router = APIRouter()

def sse(event: str, data: dict) -> str:
    return f"event: {event}\n" + f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

@router.post("/chat/stream")
def chat_stream(payload: ChatRequest):
    provider = payload.provider or "groq"

    def generate() -> Iterator[str]:
        try:
            # meta event (optional but useful)
            yield sse("meta", {"provider": provider})

            embedder, vector_store, llm, reranker, bm25, _ = get_pipeline(provider)

            answer, sources, context, status = run_rag(
                payload.query,
                embedder,
                vector_store,
                llm,
                reranker,
                bm25,
                history=[m.model_dump() for m in (payload.history or [])],
            )

            # Stream tokens (chunked for now)
            chunk_size = 20
            for i in range(0, len(answer), chunk_size):
                yield sse("token", {"delta": answer[i : i + chunk_size]})

            final = ChatResponse(
                answer=answer,
                sources=sources,
                context=truncate_context(context, 600),
                status=status,
            )

            yield sse("done", final.model_dump())

        except Exception as e:
            yield sse("error", {"message": str(e)})

    return StreamingResponse(generate(), media_type="text/event-stream")