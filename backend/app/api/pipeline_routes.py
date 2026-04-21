# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from backend.app.core.pipeline import get_pipeline, reset_pipeline, pipeline_status,

# router = APIRouter()


# class PipelineRequest(BaseModel):
#     provider: str = "groq"


# @router.post("/pipeline/load")
# def load_pipeline(payload: PipelineRequest):
#     try:
#         provider = payload.provider or "groq"
#         # embedder, vector_store, llm, reranker, bm25,
#         pipeline = get_pipeline(provider)

#         chunk_count = 0
#         if isinstance(pipeline, dict):
#             chunk_count = int(pipeline.get("chunk_count", 0))

#         return {
#             "ok": True,
#             "provider": provider,
#             "ready": True,
#             "chunk_count": chunk_count,
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Pipeline load failed: {str(e)}")


# @router.post("/pipeline/reset")
# def reset_pipeline_api(payload: PipelineRequest):
#     try:
#         provider = payload.provider or "groq"
#         reset_pipeline(provider)
#         return {"ok": True, "provider": provider, "ready": False}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Pipeline reset failed: {str(e)}")


# @router.get("/pipeline/status")
# def pipeline_status_api(provider: str = "groq"):
#     try:
#         st = pipeline_status(provider)
#         return {
#             "ok": True,
#             "provider": provider,
#             "ready": bool(st.get("ready", False)),
#             "chunk_count": int(st.get("chunk_count", 0)),
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Pipeline status failed: {str(e)}")

from fastapi import APIRouter, HTTPException
from backend.app.core.pipeline import get_pipeline, reset_pipeline, pipeline_status
from backend.app.models.pipeline_schemas import (
    PipelineRequest,
    PipelineResponse,
    PipelineResetResponse,
    PipelineStatusResponse,
)

router = APIRouter()

@router.post("/pipeline/load", response_model=PipelineResponse)
def load_pipeline(payload: PipelineRequest):
    try:
        provider = payload.provider or "groq"
        pipeline = get_pipeline(provider)

        chunk_count = 0
        if isinstance(pipeline, dict):
            chunk_count = int(pipeline.get("chunk_count", 0))

        return {
            "ok": True,
            "provider": provider,
            "ready": True,
            "chunk_count": chunk_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline load failed: {str(e)}")


@router.post("/pipeline/reset", response_model=PipelineResetResponse)
def reset_pipeline_api(payload: PipelineRequest):
    try:
        provider = payload.provider or "groq"
        reset_pipeline(provider)
        return {"ok": True, "provider": provider, "ready": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline reset failed: {str(e)}")


@router.get("/pipeline/status", response_model=PipelineStatusResponse)
def pipeline_status_api(provider: str = "groq"):
    try:
        st = pipeline_status(provider)
        return {
            "ok": True,
            "provider": provider,
            "ready": bool(st.get("ready", False)),
            "chunk_count": int(st.get("chunk_count", 0)),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline status failed: {str(e)}")