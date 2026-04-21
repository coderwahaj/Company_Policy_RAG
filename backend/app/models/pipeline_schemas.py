from pydantic import BaseModel


class PipelineRequest(BaseModel):
    provider: str = "groq"
