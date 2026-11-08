# Multi-Agent AI Research Pipeline

## Goal
A learning project to understand how multi-agent systems work: agent roles, tool calling, and structured communication between agents. Code must stay simple, readable, and easy to explain in an interview. No heavy frameworks (no LangChain, no CrewAI). Plain Python only.

## Architecture
Three agents run in sequence:
1. Researcher: uses OpenAI function calling to call a Tavily web search tool, then returns structured findings.
2. Analyst: takes the findings and returns structured insights (key points, trends, gaps).
3. Writer: takes the insights and produces a structured research report, saved as Markdown.

## Tech
- Python 3.11, managed with uv (use `uv add` for packages, `uv run` to run)
- OpenAI API for the LLM
- Tavily for web search
- Pydantic models for every agent's output, used as the contract between agents
- API keys loaded from .env with python-dotenv. Never print or log keys.

## Code level
- Plain Python: functions, the OpenAI client, Pydantic models, and a manual tool-calling loop written by hand.
- Readable over clever. Each file short and focused on one job.
- Use inheritance, *args/**kwargs or other advanced patterns only when they genuinely make the code better. When you use them, explain why in a short comment and tell me in chat.

## Structure
src layout: the code lives in an installable package, `research_pipeline`, under src/.
Import it as a package, e.g. `from research_pipeline.models import Source`.
- src/research_pipeline/models.py: Pydantic models
- src/research_pipeline/tools.py: Tavily search tool
- src/research_pipeline/agents/researcher.py, analyst.py, writer.py
- main.py: entry point that runs the pipeline (`uv run main.py`)
- outputs/: generated reports

## How to work with me
- I am learning. Build in small steps, one file at a time.
- Before writing code, explain briefly what you will do and why.
- Add short comments explaining key concepts.
