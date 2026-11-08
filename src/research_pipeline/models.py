"""Pydantic models: the data contracts passed between agents.

Each agent returns one of these models. Because Pydantic validates the data,
the next agent can trust the shape of what it receives (right fields, right types).
"""

from pydantic import BaseModel, Field


class Source(BaseModel):
    """One web search result."""

    title: str
    url: str
    content: str = Field(description="Key content or snippet from the page")


class ResearchFindings(BaseModel):
    """Researcher output: what was found on the web."""

    question: str
    sources: list[Source]
    summary: str


class AnalysisInsights(BaseModel):
    """Analyst output: what the findings mean."""

    key_points: list[str]
    trends: list[str]
    gaps: list[str] = Field(description="Gaps or open questions in the research")


class Section(BaseModel):
    """One section of the final report."""

    heading: str
    content: str


class ResearchReport(BaseModel):
    """Writer output: the final structured report."""

    title: str
    executive_summary: str
    sections: list[Section]
    conclusion: str
    sources: list[Source]
