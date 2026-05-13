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

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Legal Doc Analyzer",
    page_icon="⚖️",
    layout="wide",
)

st.title("⚖️ Legal Document Analyzer")
st.caption("Upload a contract → get instant clause extraction + natural language Q&A")

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

# ── Tab 1: Auto-extracted clauses ──────────────────────────────────────────────

with tab1:
    if st.session_state.get("clauses") is None:
        if st.button("Extract key clauses", type="primary"):
            with st.spinner("Extracting clauses... (this takes ~15 seconds)"):
                st.session_state["clauses"] = extract_clauses(st.session_state["full_text"])

    clauses = st.session_state.get("clauses")
    if clauses:
        cols = st.columns(2)
        for i, (key, label) in enumerate(CLAUSE_LABELS.items()):
            result = clauses.get(key, {})
            with cols[i % 2]:
                with st.container(border=True):
                    if result.get("found"):
                        st.markdown(f"**{label}**")
                        st.write(result.get("summary", "—"))
                        if result.get("quote"):
                            st.caption(f"> {result['quote']}")
                    else:
                        st.markdown(f"**{label}**")
                        st.caption("Not found in document")

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
