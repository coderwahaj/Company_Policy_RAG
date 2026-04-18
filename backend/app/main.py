from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import router
from backend.app.api.stream_routes import router as stream_router
app = FastAPI(title="Wamo Policy Assistant API")
from backend.app.core.pipeline import get_pipeline
from backend.app.api.pipeline_routes import router as pipeline_router

# @app.on_event("startup")
# def warmup():
#     get_pipeline("groq")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later for React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(stream_router)
app.include_router(pipeline_router)