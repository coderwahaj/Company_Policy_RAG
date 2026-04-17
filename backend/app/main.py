from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import router

app = FastAPI(title="Wamo Policy Assistant API")
from backend.app.core.pipeline import get_pipeline

@app.on_event("startup")
def warmup():
    get_pipeline("groq")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later for React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)