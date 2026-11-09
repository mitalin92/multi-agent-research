"""Writer agent: turns findings and insights into a ResearchReport, then saves it as Markdown."""

import re
from datetime import date
from pathlib import Path

from openai import OpenAI

from research_pipeline.models import AnalysisInsights, ResearchFindings, ResearchReport

MODEL = "gpt-4o-mini"

# Project root is three folders up from this file: agents/ -> research_pipeline/ -> src/ -> root.
# Using an absolute path means reports land in outputs/ no matter where we run from
# (main.py from the root, or the notebook from notebooks/).
OUTPUT_DIR = Path(__file__).resolve().parents[3] / "outputs"

SYSTEM_PROMPT = """You are a report writer.
You receive research findings and analysis insights as JSON.
Write a clear, well-structured research report: a title, an executive summary,
several sections with headings, and a conclusion.
Only use the given information. Do not invent facts."""


def run_writer(
    findings: ResearchFindings,
    insights: AnalysisInsights,
    feedback: str | None = None,
) -> ResearchReport:
    """Write the final research report from the findings and insights.

    If feedback is given (e.g. from the Streamlit app), the writer rewrites
    the report with that feedback in mind.
    """
    print("Writer: writing report...")
    client = OpenAI()  # Reads OPENAI_API_KEY from the environment (loaded from .env).

    # The writer needs both earlier outputs: the findings (facts and sources)
    # and the insights (what they mean). Both go in as JSON text.
    user_message = (
        f"Findings:\n{findings.model_dump_json()}\n\n"
        f"Insights:\n{insights.model_dump_json()}"
    )
    # Optional feedback: same findings and insights, plus the user's request for changes.
    if feedback:
        user_message += (
            f"\n\nUser feedback on the previous version: {feedback}. "
            "Rewrite the report taking this into account."
        )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    # Same pattern as the analyst: one structured call, no tools, no loop.
    completion = client.chat.completions.parse(
        model=MODEL,
        messages=messages,
        response_format=ResearchReport,
    )
    report = completion.choices[0].message.parsed
    if report is None:  # Happens if the model refuses to answer.
        raise RuntimeError("Writer did not return a report.")

    # Don't trust the LLM with sources: it could copy them wrongly or invent URLs.
    # We replace them with the real search results from the researcher,
    # so every link in the report points to a page Tavily actually found.
    report.sources = findings.sources
    return report


def report_to_markdown(report: ResearchReport) -> str:
    """Convert the report to Markdown text (used by save_report and the Streamlit app)."""
    # Build the Markdown as a list of lines, then join them at the end.
    lines = [f"# {report.title}", "", "## Executive Summary", "", report.executive_summary, ""]
    for section in report.sections:
        lines += [f"## {section.heading}", "", section.content, ""]
    lines += ["## Conclusion", "", report.conclusion, "", "## Sources", ""]
    for source in report.sources:
        lines.append(f"- [{source.title}]({source.url})")  # Markdown link syntax: [text](url)
    return "\n".join(lines) + "\n"


def report_filename(report: ResearchReport) -> str:
    """Build a filename like 2026-11-09-ai-in-agriculture.md from today's date and the title."""
    # The slug is lowercase with every run of non-letters/digits replaced by one hyphen.
    slug = re.sub(r"[^a-z0-9]+", "-", report.title.lower()).strip("-")[:60].strip("-")
    return f"{date.today().isoformat()}-{slug}.md"


def save_report(report: ResearchReport) -> Path:
    """Save the report as Markdown in outputs/ and return the file path."""
    path = OUTPUT_DIR / report_filename(report)
    OUTPUT_DIR.mkdir(exist_ok=True)  # Create outputs/ if it doesn't exist yet.
    path.write_text(report_to_markdown(report), encoding="utf-8")
    return path
