"""
RAG pipeline for legal documents.

Flow: PDF -> text -> chunks -> BM25 retrieval -> Groq LLM answer
"""

import os
from typing import Optional

import pdfplumber
from groq import Groq
from rank_bm25 import BM25Okapi

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_text(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n\n".join(pages)


def chunk_text(text: str, size: int = 300, overlap: int = 30) -> list[str]:
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i: i + size]))
        i += size - overlap
    return [c for c in chunks if len(c.strip()) > 50]


def build_index(pdf_path: str) -> tuple[list[str], BM25Okapi]:
    text = extract_text(pdf_path)
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError(
            "No text could be extracted from this PDF. "
            "Scanned or image-only PDFs are not supported — please use a text-based PDF."
        )
    tokenized = [c.lower().split() for c in chunks]
    bm25 = BM25Okapi(tokenized)
    return chunks, bm25


def retrieve(query: str, chunks: list[str], bm25: BM25Okapi, top_k: int = 3) -> list[str]:
    scores = bm25.get_scores(query.lower().split())
    top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [chunks[i] for i in top_idx]


ANSWER_PROMPT = {
    "zh": """\
You are a legal document analyst. Answer the question using ONLY the provided excerpts.
Respond in Traditional Chinese (繁體中文).
If the answer is not in the excerpts, say "此文件中未涉及此問題。"
Always quote the relevant part of the document to support your answer.

Document excerpts:
{context}

Question: {question}""",
    "en": """\
You are a legal document analyst. Answer the question using ONLY the provided excerpts.
If the answer is not in the excerpts, say "This is not addressed in the document."
Always quote the relevant part of the document to support your answer.

Document excerpts:
{context}

Question: {question}""",
}


def answer(question: str, chunks: list[str], bm25: BM25Okapi,
           retrieval_query: Optional[str] = None, lang: str = "zh") -> dict:
    relevant = retrieve(retrieval_query or question, chunks, bm25)
    context = "\n\n---\n\n".join(relevant)[:3000]
    prompt = ANSWER_PROMPT[lang].format(context=context, question=question)
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        return {"answer": response.choices[0].message.content.strip(), "sources": relevant}
    except Exception as e:
        msg = f"抱歉，處理時發生錯誤：{e}" if lang == "zh" else f"Sorry, an error occurred: {e}"
        return {"answer": msg, "sources": []}
