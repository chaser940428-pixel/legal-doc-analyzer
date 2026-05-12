"""
RAG pipeline for legal documents.

Flow: PDF → text → chunks → embeddings → retrieve → answer
"""

import os
import pickle
from pathlib import Path

import numpy as np
import pdfplumber
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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


# ── Embeddings ─────────────────────────────────────────────────────────────────

def embed(texts: list[str]) -> np.ndarray:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return np.array([item.embedding for item in response.data])


# ── Index management ───────────────────────────────────────────────────────────

def build_index(pdf_path: str) -> tuple[list[str], np.ndarray]:
    text = extract_text(pdf_path)
    chunks = chunk_text(text)
    embeddings = embed(chunks)

    with open(CACHE_FILE, "wb") as f:
        pickle.dump({"chunks": chunks, "embeddings": embeddings, "source": pdf_path}, f)

    return chunks, embeddings


def load_index() -> tuple[list[str], np.ndarray, str]:
    if not CACHE_FILE.exists():
        raise FileNotFoundError("No document indexed yet.")
    with open(CACHE_FILE, "rb") as f:
        data = pickle.load(f)
    return data["chunks"], data["embeddings"], data.get("source", "")


def clear_index() -> None:
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()


# ── Retrieval ──────────────────────────────────────────────────────────────────

def retrieve(query: str, chunks: list[str], embeddings: np.ndarray, top_k: int = 4) -> list[str]:
    q_vec = embed([query])[0]
    scores = embeddings @ q_vec / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(q_vec) + 1e-9
    )
    top_idx = np.argsort(scores)[::-1][:top_k]
    return [chunks[i] for i in top_idx]


# ── Answer generation ──────────────────────────────────────────────────────────

ANSWER_PROMPT = """\
You are a legal document analyst. Answer the question using ONLY the provided excerpts.
If the answer is not in the excerpts, say "This is not addressed in the document."
Always quote the relevant part of the document to support your answer.

Document excerpts:
{context}

Question: {question}"""


def answer(question: str, chunks: list[str], embeddings: np.ndarray) -> dict:
    relevant = retrieve(question, chunks, embeddings)
    context = "\n\n---\n\n".join(relevant)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": ANSWER_PROMPT.format(context=context, question=question)
        }],
        max_tokens=500,
        temperature=0,
    )

    return {
        "answer": response.choices[0].message.content.strip(),
        "sources": relevant,
    }
