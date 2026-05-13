"""
Streamlit UI for legal-doc-analyzer.

Run: streamlit run app.py
"""

import os
import tempfile

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from analyzer import answer, build_index, extract_text
from extractor import CLAUSE_LABELS, extract_clauses
from risk import RISK_LEVELS, assess_risks
from report import generate_report

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Legal Doc Analyzer",
    page_icon="⚖️",
    layout="wide",
)

st.title("⚖️ Legal Document Analyzer")
st.caption("Upload a contract → get instant clause extraction + risk assessment + natural language Q&A")

# ── Sidebar: upload ────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Document")
    uploaded = st.file_uploader("Upload PDF contract", type=["pdf"])

    if uploaded:
        if st.button("Analyze document", type="primary", use_container_width=True):
            with st.spinner("Reading and indexing document..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded.read())
                    tmp_path = tmp.name

                try:
                    chunks, bm25 = build_index(tmp_path)
                    full_text = extract_text(tmp_path)
                    os.unlink(tmp_path)

                    st.session_state["chunks"] = chunks
                    st.session_state["bm25"] = bm25
                    st.session_state["full_text"] = full_text
                    st.session_state["filename"] = uploaded.name
                    st.session_state["clauses"] = None
                    st.session_state["risks"] = None
                    st.session_state["chat"] = []

                    st.success(f"Indexed {len(chunks)} sections")
                except ValueError as e:
                    os.unlink(tmp_path)
                    st.error(str(e))

    if "filename" in st.session_state:
        st.info(f"Active: {st.session_state['filename']}")

    st.divider()
    st.caption("Built with Groq + Streamlit\ngithub.com/chaser940428-pixel/legal-doc-analyzer")

# ── Main area ──────────────────────────────────────────────────────────────────

if "chunks" not in st.session_state:
    st.info("Upload a PDF contract in the sidebar to get started.")
    st.stop()

tab1, tab2 = st.tabs(["Key Clauses", "Ask Anything"])

# ── Tab 1: Auto-extracted clauses + risk assessment ────────────────────────────

with tab1:
    if st.session_state.get("clauses") is None:
        if st.button("Extract key clauses", type="primary"):
            with st.spinner("Extracting clauses and assessing risks... (~20 seconds)"):
                clauses = extract_clauses(st.session_state["full_text"])
                risks = assess_risks(clauses)
                st.session_state["clauses"] = clauses
                st.session_state["risks"] = risks

    clauses = st.session_state.get("clauses")
    risks = st.session_state.get("risks") or {}

    if clauses:
        # Overall risk banner
        overall = risks.get("overall", {})
        if overall:
            level = overall.get("level", "low")
            summary = overall.get("summary", "")
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(level, "⚪")
            label = {"high": "High Risk", "medium": "Medium Risk", "low": "Low Risk"}.get(level, "")
            if level == "high":
                st.error(f"{icon} **Overall Risk: {label}** — {summary}")
            elif level == "medium":
                st.warning(f"{icon} **Overall Risk: {label}** — {summary}")
            else:
                st.success(f"{icon} **Overall Risk: {label}** — {summary}")

        st.divider()

        # Clause cards
        cols = st.columns(2)
        for i, (key, label) in enumerate(CLAUSE_LABELS.items()):
            result = clauses.get(key, {})
            risk = risks.get(key, {})
            risk_level = risk.get("level", "none")
            risk_display = RISK_LEVELS.get(risk_level, "")

            with cols[i % 2]:
                with st.container(border=True):
                    col_title, col_badge = st.columns([3, 1])
                    with col_title:
                        st.markdown(f"**{label}**")
                    with col_badge:
                        st.markdown(f"<div style='text-align:right'>{risk_display}</div>", unsafe_allow_html=True)

                    if result.get("found"):
                        st.write(result.get("summary", "—"))
                        if result.get("quote"):
                            st.caption(f"> {result['quote']}")
                    else:
                        st.caption("Not found in document")

                    if risk.get("reason"):
                        st.caption(f"_{risk['reason']}_")

        st.divider()

        # Download report
        report_bytes = generate_report(
            st.session_state.get("filename", "document.pdf"),
            clauses,
            risks,
            CLAUSE_LABELS,
        )
        st.download_button(
            label="Download Analysis Report (PDF)",
            data=report_bytes,
            file_name="legal_analysis_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

# ── Tab 2: Q&A ─────────────────────────────────────────────────────────────────

with tab2:
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    for msg in st.session_state["chat"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("sources"):
                with st.expander("Source excerpts"):
                    for i, src in enumerate(msg["sources"], 1):
                        st.caption(f"[{i}] {src[:300]}...")

    question = st.chat_input("Ask anything about this contract...")

    if question:
        st.session_state["chat"].append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching document..."):
                result = answer(
                    question,
                    st.session_state["chunks"],
                    st.session_state["bm25"],
                )
            st.write(result["answer"])
            with st.expander("Source excerpts"):
                for i, src in enumerate(result["sources"], 1):
                    st.caption(f"[{i}] {src[:300]}...")

        st.session_state["chat"].append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        })
