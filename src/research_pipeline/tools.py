"""Tools the agents can use. Right now: one web search tool backed by Tavily."""

import os

from dotenv import load_dotenv
from tavily import TavilyClient

from research_pipeline.models import Source

# Read API keys from .env into environment variables (never print them).
load_dotenv()


def web_search(query: str, max_results: int = 5) -> list[Source]:
    """Search the web with Tavily and return the results as Source objects."""
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = client.search(query=query, max_results=max_results)

    # Tavily returns a dict like {"results": [{"title", "url", "content", ...}, ...]}.
    # We convert each result into our own Source model, so other code
    # never depends on Tavily's raw format.
    return [
        Source(title=r["title"], url=r["url"], content=r["content"])
        for r in response["results"]
    ]


# The tool schema tells the LLM that this tool exists and how to call it.
# The LLM never runs code itself: it replies "call web_search with this query",
# and our code runs the real function and sends the results back.
WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for up-to-date information on a topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query, e.g. 'latest trends in solar energy 2026'",
                }
            },
            "required": ["query"],
        },
    },
}
