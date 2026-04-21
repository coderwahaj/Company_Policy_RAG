from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from backend.app.core.pipeline import get_pipeline, reset_pipeline, pipeline_status
from backend.app.models.pipeline_schemas import PipelineRequest

router = APIRouter()


@router.post("/pipeline/load")
def load_pipeline(payload: PipelineRequest):
    try:
        provider = payload.provider or "groq"
        pipeline = get_pipeline(provider)

        chunk_count = 0
        if isinstance(pipeline, dict):
            chunk_count = int(pipeline.get("chunk_count", 0))

        return JSONResponse(
            status_code=201,
            content={
                "provider": provider,
                "ready": True,
                "chunk_count": chunk_count,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline load failed: {str(e)}")


@router.post("/pipeline/reset")
def reset_pipeline_api(payload: PipelineRequest):
    try:
        provider = payload.provider or "groq"
        reset_pipeline(provider)
        return JSONResponse(
            status_code=200,
            content={"provider": provider, "ready": False},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline reset failed: {str(e)}")


@router.get("/pipeline/status")
def pipeline_status_api(provider: str = "groq"):
    try:
        st = pipeline_status(provider)
        return JSONResponse(
            status_code=200,
            content={
                "provider": provider,
                "ready": bool(st.get("ready", False)),
                "chunk_count": int(st.get("chunk_count", 0)),
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline status failed: {str(e)}")