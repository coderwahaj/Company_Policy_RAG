from pydantic import BaseModel

class PipelineRequest(BaseModel):
    provider: str = "groq"

class PipelineResponse(BaseModel):
    ok: bool
    provider: str
    ready: bool
    chunk_count: int

class PipelineResetResponse(BaseModel):
    ok: bool
    provider: str
    ready: bool

class PipelineStatusResponse(BaseModel):
    ok: bool
    provider: str
    ready: bool
    chunk_count: int