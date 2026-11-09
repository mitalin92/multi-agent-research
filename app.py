"""Streamlit web app for the research pipeline (Researcher -> Analyst -> Writer).

Run with:
    uv run streamlit run app.py
"""

import streamlit as st

from research_pipeline.agents.analyst import run_analyst
from research_pipeline.agents.researcher import run_researcher
from research_pipeline.agents.writer import report_filename, report_to_markdown, run_writer

# --- How Streamlit works, and why we need st.session_state ---
# Streamlit runs this whole file from top to bottom every time the user does
# something (clicks a button, types in a box). Normal variables are lost on each rerun.
# st.session_state is a dictionary that Streamlit keeps between reruns, so it is
# the app's "memory". We save the agents' outputs there so we don't lose them
# (and don't pay for the API calls again) when the user clicks the next button.

st.title("Multi-Agent Research Pipeline")
st.write(
    "Three AI agents work in sequence:\n"
    "1. **Researcher** searches the web (Tavily) and collects findings.\n"
    "2. **Analyst** turns the findings into key points, trends and gaps.\n"
    "3. **Writer** writes a structured research report."
)

# st.chat_input draws a chat-style box pinned to the bottom of the page.
# It returns the typed text only on the rerun right after the user presses Enter,
# and None on every other rerun. It never submits an empty message.
question = st.chat_input("Ask me a research question...")

if question:
    # st.status shows a collapsible box with a spinner, then a tick when it's done.
    with st.status("Researcher: searching the web...") as status:
        findings = run_researcher(question)
        status.update(label=f"Researcher: found {len(findings.sources)} sources", state="complete")

    with st.status("Analyst: analysing the findings...") as status:
        insights = run_analyst(findings)
        status.update(label="Analyst: insights ready", state="complete")

    with st.status("Writer: writing the report...") as status:
        report = run_writer(findings, insights)
        status.update(label="Writer: report ready", state="complete")

    # Save all three outputs so they survive the next rerun.
    st.session_state.findings = findings
    st.session_state.insights = insights
    st.session_state.report = report

# Only show the report section once a report exists in session_state.
if "report" in st.session_state:
    report = st.session_state.report
    markdown = report_to_markdown(report)

    st.divider()
    st.markdown(markdown)
    st.download_button(
        "Download report (.md)",
        data=markdown,
        file_name=report_filename(report),
        mime="text/markdown",
    )

    # --- Feedback loop: rerun only the Writer, reusing the saved findings and insights ---
    st.divider()
    feedback = st.text_area("How should the report be improved?")
    if st.button("Improve report"):
        if not feedback.strip():
            st.warning("Please describe what to improve.")
        else:
            with st.status("Writer: rewriting the report...") as status:
                st.session_state.report = run_writer(
                    st.session_state.findings,
                    st.session_state.insights,
                    feedback=feedback,
                )
                status.update(label="Writer: new version ready", state="complete")
            # The old report was already drawn above this button, so we ask
            # Streamlit to run the file again from the top to show the new one.
            st.rerun()
