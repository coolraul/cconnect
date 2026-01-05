from typing import cast

from openai.types.chat import ChatCompletionFunctionToolParam

# Tell the type checker this dict conforms to OpenAI's tool schema.
search_videos_tool: ChatCompletionFunctionToolParam = cast(
    ChatCompletionFunctionToolParam,
    {
        "type": "function",
        "function": {
            "name": "search_videos",
            "description": "Search for exercise instruction videos on YouTube.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search terms describing the exercise video the user is asking for.",
                    }
                },
                "required": ["query"],
            },
        },
    },
)
