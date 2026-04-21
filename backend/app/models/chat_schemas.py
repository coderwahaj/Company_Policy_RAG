# from typing import List, Optional
# from pydantic import BaseModel


# class Message(BaseModel):
#     role: str
#     content: str


# class ChatRequest(BaseModel):
#     query: str
#     history: Optional[List[Message]] = None
#     provider: Optional[str] = None


# class ChatResponse(BaseModel):
#     answer: str
#     sources: List[str]
#     context: str
#     status: str
# class PipelineRequest(BaseModel):
#     provider: str = "groq"


# class PipelineResponse(BaseModel):
#     ok: bool
#     provider: str
#     ready: bool
#     chunk_count: int


# class PipelineResetResponse(BaseModel):
#     ok: bool
#     provider: str
#     ready: bool


# class PipelineStatusResponse(BaseModel):
#     ok: bool
#     provider: str
#     ready: bool
#     chunk_count: int

from typing import List, Optional
from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    query: str
    history: Optional[List[Message]] = None
    provider: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    context: str
    status: str
