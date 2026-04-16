from fastapi import APIRouter
from backend.app.models.schemas import ChatRequest, ChatResponse
from backend.app.core.pipeline import get_pipeline
from backend.app.core.rag_service import run_rag, truncate_context

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    provider = payload.provider or "groq"
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
    return ChatResponse(
        answer=answer,
        sources=sources,
        context=truncate_context(context, 600),
        status=status,
    )