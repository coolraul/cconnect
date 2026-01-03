from typing import Optional

import logging
import json

from fastapi import FastAPI, HTTPException, Header
from openai import OpenAI

from app.config import get_env
from app.schemas import EchoRequest, EchoResponse, ChatRequest, ChatResponse
from app.openai_tools import search_videos_tool
from app.youtube import youtube_search


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
def chat(req: ChatRequest):
    # Convert Pydantic objects to plain dicts for OpenAI
    messages = [m.model_dump() for m in req.messages]

    # 1) First call: allow tool usage
    first = openai_client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=[search_videos_tool],
        tool_choice="auto",
    )

    msg = first.choices[0].message

    # If no tool calls, return direct response
    if not msg.tool_calls:
        return ChatResponse(reply=msg.content or "")

    # 2) Handle tool calls (support multiple, but you’ll likely have one)
    tool_messages = []
    for tc in msg.tool_calls:
        tool_name = tc.function.name
        tool_args = json.loads(tc.function.arguments)

        if tool_name == "search_videos":
            print("calling tool!!")

            query = tool_args["query"]
            videos = youtube_search(query, max_results=3)
            tool_output = json.dumps(videos)
        else:
            tool_output = json.dumps({"error": f"Unknown tool: {tool_name}"})

        tool_messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "name": tool_name,
            "content": tool_output,
        })

    # 3) Second call: provide the tool outputs so model can answer
    second = openai_client.chat.completions.create(
        model=model_name,
        messages=[
            *messages,
            msg,              # assistant message containing tool_calls
            *tool_messages,   # tool outputs
        ],
    )

    final_msg = second.choices[0].message
    return ChatResponse(reply=final_msg.content or "")