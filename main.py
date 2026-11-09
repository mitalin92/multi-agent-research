"""Entry point: runs the research pipeline (Researcher -> Analyst -> Writer).

Usage:
    uv run main.py "What are the latest trends in AI for agriculture?"
"""

import argparse

from research_pipeline.agents.analyst import run_analyst
from research_pipeline.agents.researcher import run_researcher
from research_pipeline.agents.writer import run_writer, save_report


def main():
    # argparse reads arguments from the command line and builds a --help message for us.
    parser = argparse.ArgumentParser(description="Run the multi-agent research pipeline.")
    parser.add_argument("question", help="The research question to investigate.")
    args = parser.parse_args()

    # Each agent's Pydantic output is the input for the next agent.
    print("Step 1/3: Researching...")
    findings = run_researcher(args.question)

    print("Step 2/3: Analysing...")
    insights = run_analyst(findings)

    print("Step 3/3: Writing...")
    report = run_writer(findings, insights)
    path = save_report(report)

    print(f"Report saved to: {path}")


if __name__ == "__main__":
    main()
