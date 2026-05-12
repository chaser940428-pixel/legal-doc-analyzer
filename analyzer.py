"""
RAG pipeline for legal documents.

Flow: PDF -> text -> chunks -> BM25 retrieval -> Gemini answer
Uses BM25 (free, no API needed) for retrieval + Google Gemini for generation.
"""

import os
import pickle
from pathlib import Path

import google.generativeai as genai
import pdfplumber
from rank_bm25 import BM25Okapi

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

CACHE_FILE = Path(".doc_cache.pkl")


# ── Text extraction ────────────────────────────────────────────────────────────

def extract_text(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n\n".join(pages)


# ── Chunking ───────────────────────────────────────────────────────────────────

def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i: i + size]))
        i += size - overlap
    return [c for c in chunks if len(c.strip()) > 50]


# ── Index management ───────────────────────────────────────────────────────────

def build_index(pdf_path: str) -> tuple[list[str], BM25Okapi]:
    text = extract_text(pdf_path)
    chunks = chunk_text(text)
    tokenized = [c.lower().split() for c in chunks]
    bm25 = BM25Okapi(tokenized)

    with open(CACHE_FILE, "wb") as f:
        pickle.dump({"chunks": chunks, "bm25": bm25, "source": pdf_path}, f)

    return chunks, bm25


def load_index() -> tuple[list[str], BM25Okapi, str]:
    if not CACHE_FILE.exists():
        raise FileNotFoundError("No document indexed yet.")
    with open(CACHE_FILE, "rb") as f:
        data = pickle.load(f)
    return data["chunks"], data["bm25"], data.get("source", "")


def clear_index() -> None:
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()


# ── Retrieval ──────────────────────────────────────────────────────────────────

def retrieve(query: str, chunks: list[str], bm25: BM25Okapi, top_k: int = 4) -> list[str]:
    scores = bm25.get_scores(query.lower().split())
    top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [chunks[i] for i in top_idx]


# ── Answer generation ──────────────────────────────────────────────────────────

ANSWER_PROMPT = """\
You are a legal document analyst. Answer the question using ONLY the provided excerpts.
If the answer is not in the excerpts, say "This is not addressed in the document."
Always quote the relevant part of the document to support your answer.

Document excerpts:
{context}

Question: {question}"""


def answer(question: str, chunks: list[str], bm25: BM25Okapi) -> dict:
    relevant = retrieve(question, chunks, bm25)
    context = "\n\n---\n\n".join(relevant)

    response = model.generate_content(
        ANSWER_PROMPT.format(context=context, question=question)
    )

    return {
        "answer": response.text.strip(),
        "sources": relevant,
    }
