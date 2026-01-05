from pydantic import BaseModel
from typing import List, Literal, cast
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)


Role = Literal["system", "user", "assistant"]


class ChatMessage(BaseModel):
    role: Role
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    reply: str


def to_openai_messages(req: ChatRequest) -> List[ChatCompletionMessageParam]:
    messages: List[ChatCompletionMessageParam] = []
    for message in req.messages:
        raw = message.model_dump()
        if message.role == "assistant":
            messages.append(cast(ChatCompletionAssistantMessageParam, raw))
        elif message.role == "user":
            messages.append(cast(ChatCompletionUserMessageParam, raw))
        else:  # system
            messages.append(cast(ChatCompletionSystemMessageParam, raw))

    return messages
