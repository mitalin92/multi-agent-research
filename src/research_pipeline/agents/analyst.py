"""Analyst agent: turns ResearchFindings into AnalysisInsights with a single LLM call."""

from openai import OpenAI

from research_pipeline.models import AnalysisInsights, ResearchFindings

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """You are a research analyst.
You receive research findings as JSON: a question, a list of sources, and a summary.
Identify the key points, the trends, and the gaps or open questions in the research.
Only use information from the findings. Do not invent facts."""


def run_analyst(findings: ResearchFindings) -> AnalysisInsights:
    """Analyse the researcher's findings and return structured insights."""
    print("Analyst: analysing findings...")
    client = OpenAI()  # Reads OPENAI_API_KEY from the environment (loaded from .env).

    # The findings go in as JSON text. This is the "contract" in action:
    # the analyst receives exactly the shape the researcher promised to return.
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": findings.model_dump_json()},
    ]

    # No tools and no loop: the analyst only reasons over data it is given,
    # so one structured call is enough. parse() returns a validated AnalysisInsights.
    completion = client.chat.completions.parse(
        model=MODEL,
        messages=messages,
        response_format=AnalysisInsights,
    )
    insights = completion.choices[0].message.parsed
    if insights is None:  # Happens if the model refuses to answer.
        raise RuntimeError("Analyst did not return insights.")
    return insights
