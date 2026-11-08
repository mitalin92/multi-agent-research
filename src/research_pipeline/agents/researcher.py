"""Researcher agent: searches the web with a tool-calling loop, returns ResearchFindings."""

import json
from datetime import date

from openai import OpenAI

from research_pipeline.models import ResearchFindings
from research_pipeline.tools import WEB_SEARCH_TOOL, web_search

MODEL = "gpt-4o-mini"
MAX_SEARCHES = 3  # Hard cap on searches, to control cost.

SYSTEM_PROMPT = f"""You are a research agent. Today is {date.today()}.
Use the web_search tool to find current, reliable information on the user's question.
Run focused searches (at most {MAX_SEARCHES}), then stop searching.
Only cite sources that appeared in your search results."""


def run_researcher(question: str) -> ResearchFindings:
    """Answer a question by searching the web, then return structured findings."""
    client = OpenAI()  # Reads OPENAI_API_KEY from the environment (loaded from .env).

    # The conversation so far. Every round of the loop adds to this list,
    # so the LLM always sees its earlier searches and their results.
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    searches = 0

    # --- The agent loop ---
    while searches < MAX_SEARCHES:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=[WEB_SEARCH_TOOL],
        )
        message = response.choices[0].message

        # No tool call means the LLM thinks it has enough information: stop looping.
        if not message.tool_calls:
            break

        # Keep the LLM's tool request in the history. The API requires it
        # to appear before the matching tool results.
        messages.append(message)

        # The LLM can request several searches at once, so handle each one.
        for tool_call in message.tool_calls:
            # The LLM sends the arguments as a JSON string, e.g. '{"query": "..."}'.
            query = json.loads(tool_call.function.arguments)["query"]

            if searches < MAX_SEARCHES:
                print(f"Searching: {query}")
                sources = web_search(query)
                result = json.dumps([source.model_dump() for source in sources])
                searches += 1
            else:
                # Every tool call needs an answer, even when we skip the search.
                result = "Search limit reached. No search was run."

            # A "tool" message carries the result back. tool_call_id links it
            # to the request it answers.
            messages.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": result}
            )

    # --- Final structured answer ---
    # parse() makes the LLM reply in the exact shape of ResearchFindings,
    # and the SDK turns that reply into a validated Pydantic object.
    # No tools are passed here, so the LLM must answer instead of searching.
    completion = client.chat.completions.parse(
        model=MODEL,
        messages=messages,
        response_format=ResearchFindings,
    )
    findings = completion.choices[0].message.parsed
    if findings is None:  # Happens if the model refuses to answer.
        raise RuntimeError("Researcher did not return findings.")
    return findings
