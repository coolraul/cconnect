import logging
import json

from fastapi import FastAPI 
from openai import OpenAI

from app.config import get_env
from app.schemas import ChatRequest, ChatResponse, to_openai_messages
from app.openai_tools import search_videos_tool
from app.youtube import youtube_search
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageFunctionToolCallParam,
    ChatCompletionMessageParam,
    ChatCompletionToolMessageParam,
)


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



@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    messages: list[ChatCompletionMessageParam] = to_openai_messages(req)

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
    tool_call_params: list[ChatCompletionMessageFunctionToolCallParam] = []
    tool_messages: list[ChatCompletionToolMessageParam] = []
    for tc in msg.tool_calls:
        if tc.type != "function":
            logger.warning("Unsupported tool call type: %s", tc.type)
            continue

        func_call = tc.function
        tool_name = func_call.name
        tool_args = json.loads(func_call.arguments)

        if tool_name == "search_videos":

            query = tool_args["query"]
            print(f"calling tool!! query = {query}")

            videos = youtube_search(query, max_results=3)
            tool_output = json.dumps(videos)
        else:
            tool_output = json.dumps({"error": f"Unknown tool: {tool_name}"})

        tool_call_params.append(
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": func_call.arguments,
                },
            }
        )

        tool_messages.append(
            {
                "role": "tool",
                "tool_call_id": tc.id,
                "content": tool_output,
            }
        )

    # 3) Second call: provide the tool outputs so model can answer
    assistant_message: ChatCompletionAssistantMessageParam = {
        "role": "assistant",
        "content": msg.content,
        "tool_calls": tool_call_params,
    }

    second = openai_client.chat.completions.create(
        model=model_name,
        messages=[
            *messages,
            assistant_message,  # assistant message containing tool_calls
            *tool_messages,     # tool outputs
        ],
    )

    final_msg = second.choices[0].message
    return ChatResponse(reply=final_msg.content or "")
