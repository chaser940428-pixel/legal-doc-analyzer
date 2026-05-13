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

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer    {visibility: hidden;}
.block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

SAMPLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_contract.pdf")

# ── Helper ─────────────────────────────────────────────────────────────────────

def _index_file(path: str, name: str) -> bool:
    """Build BM25 index from a PDF and store results in session_state."""
    try:
        chunks, bm25 = build_index(path)
        full_text = extract_text(path)
        st.session_state.update({
            "chunks":   chunks,
            "bm25":     bm25,
            "full_text": full_text,
            "filename": name,
            "clauses":  None,
            "risks":    None,
            "chat":     [],
            "report":   None,
        })
        return True
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Failed to process document: {e}")
    return False

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Document")
    uploaded = st.file_uploader("Upload PDF contract", type=["pdf"])

    if uploaded:
        if st.button("Analyze document", type="primary", use_container_width=True):
            with st.spinner("Reading and indexing document…"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded.read())
                    tmp_path = tmp.name
                try:
                    success = _index_file(tmp_path, uploaded.name)
                finally:
                    os.unlink(tmp_path)
                if success:
                    st.success(f"Indexed {len(st.session_state['chunks'])} sections")
                    st.rerun()

    st.divider()

    if st.button("▶ Try sample contract", use_container_width=True,
                 help="Load a pre-built software development agreement to explore the tool"):
        if os.path.exists(SAMPLE_PATH):
            with st.spinner("Loading sample…"):
                if _index_file(SAMPLE_PATH, "sample_contract.pdf"):
                    st.rerun()
        else:
            st.error("Sample file not found.")

    if "filename" in st.session_state:
        st.info(f"Active: **{st.session_state['filename']}**")

    st.divider()
    st.caption("Powered by [Groq](https://groq.com) · [GitHub](https://github.com/chaser940428-pixel/legal-doc-analyzer)")

# ── Landing page (no document loaded) ─────────────────────────────────────────

if "chunks" not in st.session_state:
    st.markdown("## ⚖️ Legal Document Analyzer")
    st.markdown(
        "Upload any contract PDF and get **clause extraction**, "
        "**risk scoring**, and an **AI Q&A interface** in under 30 seconds."
    )
    st.markdown("")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info(
            "**📋 Clause Extraction**\n\n"
            "Automatically identifies 7 key clause types: termination, "
            "payment, liability, IP ownership, confidentiality, governing law, and duration."
        )
    with c2:
        st.warning(
            "**⚠️ Risk Assessment**\n\n"
            "Flags high, medium, and low-risk provisions with specific reasons "
            "and an overall contract risk score."
        )
    with c3:
        st.success(
            "**💬 Ask Anything**\n\n"
            "Ask questions in plain language — *\"What happens if I miss a payment?\"* "
            "— answered using only your document."
        )

    st.markdown("---")
    st.markdown(
        "**Get started:** upload a PDF in the sidebar, or click **▶ Try sample contract** "
        "to explore with a pre-built software development agreement."
    )
    st.caption(
        "ℹ️ This tool is for informational purposes only and does not constitute legal advice. "
        "Consult a qualified attorney for legal matters."
    )
    st.stop()

# ── Document loaded ────────────────────────────────────────────────────────────

st.markdown(f"### {st.session_state['filename']}")
tab1, tab2 = st.tabs(["📋 Key Clauses & Risk", "💬 Ask Anything"])

# ── Tab 1: Clause extraction + risk assessment ─────────────────────────────────

with tab1:
    if st.session_state.get("clauses") is None:
        st.markdown("Document indexed and ready.")
        if st.button("Extract key clauses", type="primary"):
            with st.spinner("Extracting clauses and assessing risks… (~20 seconds)"):
                clauses = extract_clauses(
                    st.session_state["full_text"],
                    chunks=st.session_state["chunks"],
                    bm25=st.session_state["bm25"],
                )
                risks = assess_risks(clauses)
                st.session_state["clauses"] = clauses
                st.session_state["risks"] = risks

    clauses = st.session_state.get("clauses")
    risks   = st.session_state.get("risks") or {}

    if clauses:
        if risks.get("_error"):
            st.warning(f"Risk assessment failed: {risks['_error']}")

        overall = risks.get("overall", {})
        if overall:
            level   = overall.get("level", "low")
            summary = overall.get("summary", "")
            icon  = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(level, "⚪")
            label = {"high": "High Risk", "medium": "Medium Risk", "low": "Low Risk"}.get(level, "")
            banner = f"{icon} **Overall Risk: {label}** — {summary}"
            if level == "high":
                st.error(banner)
            elif level == "medium":
                st.warning(banner)
            else:
                st.success(banner)

        st.divider()

        cols = st.columns(2)
        for i, (key, label) in enumerate(CLAUSE_LABELS.items()):
            result     = clauses.get(key, {})
            risk       = risks.get(key, {})
            risk_level = risk.get("level", "none")
            risk_badge = RISK_LEVELS.get(risk_level, "")

            with cols[i % 2]:
                with st.container(border=True):
                    col_title, col_badge = st.columns([3, 1])
                    with col_title:
                        st.markdown(f"**{label}**")
                    with col_badge:
                        st.markdown(
                            f"<div style='text-align:right'>{risk_badge}</div>",
                            unsafe_allow_html=True,
                        )

                    if result.get("found"):
                        st.write(result.get("summary", "—"))
                        if result.get("quote"):
                            st.caption(f"> {result['quote']}")
                    else:
                        st.caption("Not found in document")

                    if risk.get("reason"):
                        st.caption(f"_{risk['reason']}_")

        st.divider()

        if st.session_state.get("report") is None:
            st.session_state["report"] = generate_report(
                st.session_state.get("filename", "document.pdf"),
                clauses,
                risks,
                CLAUSE_LABELS,
            )
        st.download_button(
            label="⬇ Download Analysis Report (PDF)",
            data=st.session_state["report"],
            file_name="legal_analysis_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.caption(
            "ℹ️ AI-generated analysis for informational purposes only. "
            "Not legal advice."
        )

# ── Tab 2: Q&A ─────────────────────────────────────────────────────────────────

with tab2:
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if not st.session_state["chat"]:
        st.markdown("**Ask anything about this contract in plain language.**")
        st.markdown("Try an example:")
        examples = [
            "What happens if I miss a payment?",
            "Who owns the code after the contract ends?",
            "How much notice is required to terminate?",
            "What is the liability cap?",
        ]
        ex_cols = st.columns(2)
        for j, ex in enumerate(examples):
            with ex_cols[j % 2]:
                if st.button(ex, key=f"ex_{j}", use_container_width=True):
                    with st.spinner("Searching document…"):
                        result = answer(ex, st.session_state["chunks"], st.session_state["bm25"])
                    st.session_state["chat"].append({"role": "user", "content": ex})
                    st.session_state["chat"].append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result["sources"],
                    })
                    st.rerun()
        st.markdown("---")

    for msg in st.session_state["chat"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("sources"):
                with st.expander("Source excerpts"):
                    for i, src in enumerate(msg["sources"], 1):
                        st.caption(f"[{i}] {src[:300]}…")

    question = st.chat_input("Ask about this contract…")

    if question:
        st.session_state["chat"].append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching document…"):
                result = answer(question, st.session_state["chunks"], st.session_state["bm25"])
            st.write(result["answer"])
            if result["sources"]:
                with st.expander("Source excerpts"):
                    for i, src in enumerate(result["sources"], 1):
                        st.caption(f"[{i}] {src[:300]}…")

        st.session_state["chat"].append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        })
