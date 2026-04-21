from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import router
from backend.app.api.stream_routes import router as stream_router
from backend.app.core.pipeline import get_pipeline
from backend.app.api.pipeline_routes import router as pipeline_router

app = FastAPI(title="Wamo Policy Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(stream_router)
app.include_router(pipeline_router)