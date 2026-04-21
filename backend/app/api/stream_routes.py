import json
from typing import Iterator
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.app.models.chat_schemas import ChatRequest
from backend.app.core.pipeline import get_pipeline
from backend.app.core.rag_service import run_rag_stream, truncate_context

router = APIRouter()

def sever_sent_events(event: str, data: dict) -> str:
    return f"event: {event}\n" + f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

@router.post("/chat/stream")
def chat_stream(payload: ChatRequest):
    provider = payload.provider or "groq"

    def generate() -> Iterator[str]:
        try:
            #metadata event
            yield sever_sent_events("meta", {"provider": provider})

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
                    yield sever_sent_events("token", data)
                elif event == "done":
                    data["context"] = truncate_context(data.get("context", ""), 600)
                    yield sever_sent_events("done", data)
                elif event == "error":
                    yield sever_sent_events("error", data)

        except Exception as e:
            yield sever_sent_events("error", {"message": str(e)})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
