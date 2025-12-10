from typing import Optional

import logging

from fastapi import FastAPI, HTTPException, Header
from openai import OpenAI

from app.config import get_env
from app.schemas import EchoRequest, EchoResponse, ChatRequest, ChatResponse

app = FastAPI(
    title="Senior Support API",
    version="0.1.0"
)

logger = logging.getLogger("uvicorn.error")


@app.get("/health")
def health_check():
    return {"status": "ok"}


openai_client = OpenAI(api_key=get_env("OPENAI_API_KEY"))
model_name = get_env("OPENAI_MODEL", "gpt-4o-mini")
chat_shared_secret = get_env("CHAT_SHARED_SECRET")

if not chat_shared_secret:
    raise RuntimeError("CHAT_SHARED_SECRET must be set")


@app.post("/echo", response_model=EchoResponse)
def echo(payload: EchoRequest):
    """
    Test endpoint for Replit JS client.
    Just echoes whatever JSON is sent.
    """
    return {"echoed": payload.data}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, x_chat_secret: Optional[str] = Header(default=None, alias="X-Chat-Secret")):
    if x_chat_secret != chat_shared_secret:
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info("Client message contents: %s", [message.content for message in payload.messages])

    try:
        completion = openai_client.chat.completions.create(
            model=model_name,
            messages=[message.model_dump() for message in payload.messages]
        )
    except Exception as exc:
        # Surface an actionable HTTP error when the upstream call fails.
        raise HTTPException(status_code=502, detail="OpenAI request failed") from exc

    if not completion.choices:
        raise HTTPException(status_code=502, detail="OpenAI returned no choices")

    return {"response": completion.choices[0].message.content}
