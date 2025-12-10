from pydantic import BaseModel
from typing import Any, Dict, List


class EchoRequest(BaseModel):
    data: Dict[str, Any]


class EchoResponse(BaseModel):
    echoed: Dict[str, Any]


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    response: str
