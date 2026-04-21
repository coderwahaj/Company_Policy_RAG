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
