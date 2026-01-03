search_videos_tool = {
    "type": "function",
    "function": {
        "name": "search_videos",
        "description": "Search for exercise instruction videos on YouTube.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search terms describing the exercise video the user is asking for."
                }
            },
            "required": ["query"]
        }
    }
}