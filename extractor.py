"""
Structured clause extraction using Groq LLM.

Uses BM25 retrieval to find the most relevant chunks per clause type,
so extraction works correctly regardless of document length.
"""

import json
import os
from typing import Optional

from groq import Groq
from rank_bm25 import BM25Okapi

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CLAUSE_LABELS = {
    "termination": "Termination",
    "payment_terms": "Payment Terms",
    "liability": "Liability & Indemnification",
    "confidentiality": "Confidentiality",
    "governing_law": "Governing Law",
    "ip_ownership": "IP Ownership",
    "term_duration": "Contract Duration",
}

# Keywords used to retrieve relevant chunks per clause type.
# Each clause can have multiple queries to ensure comprehensive coverage.
CLAUSE_KEYWORDS: dict[str, list[str]] = {
    "termination": [
        "termination terminate end agreement notice cancel",
    ],
    "payment_terms": [
        "payment fee retainer invoice monthly milestone",
        "late penalty interest overdue per month annum",  # separate query to catch late-payment clauses
    ],
    "liability": [
        "liability indemnify indemnification damages limit cap responsible",
    ],
    "confidentiality": [
        "confidential confidentiality non-disclosure secret proprietary",
    ],
    "governing_law": [
        "governing law jurisdiction court arbitration dispute",
    ],
    "ip_ownership": [
        "intellectual property IP ownership copyright work product assign",
    ],
    "term_duration": [
        "term duration period commencement expiry renewal effective date",
    ],
}

_EXTRACT_PROMPT_BASE = """\
You are a legal analyst. Read the contract excerpts below and extract the following clauses.

For each clause, return a JSON object with:
- "found": true if the clause exists in the excerpts, false if not
- "summary": 1-2 sentence plain-language summary{lang_note} (null if not found). IMPORTANT: always include specific numbers, percentages, rates, and deadlines (e.g. "1.5% per month interest", "14-day notice period").
- "quote": the most relevant verbatim excerpt (null if not found). Prefer quotes that contain specific rates, amounts, or conditions over general statements.

Return ONLY valid JSON with this exact structure, no markdown:
{{
  "termination": {{"found": ..., "summary": "...", "quote": "..."}},
  "payment_terms": {{"found": ..., "summary": "...", "quote": "..."}},
  "liability": {{"found": ..., "summary": "...", "quote": "..."}},
  "confidentiality": {{"found": ..., "summary": "...", "quote": "..."}},
  "governing_law": {{"found": ..., "summary": "...", "quote": "..."}},
  "ip_ownership": {{"found": ..., "summary": "...", "quote": "..."}},
  "term_duration": {{"found": ..., "summary": "...", "quote": "..."}}
}}

Contract excerpts:
{text}"""


def _build_clause_context(chunks: list[str], bm25: BM25Okapi, top_k: int = 2) -> str:
    """Retrieve the most relevant chunks for each clause type and deduplicate."""
    seen: set[int] = set()
    selected: list[str] = []

    for queries in CLAUSE_KEYWORDS.values():
        for query in queries:
            scores = bm25.get_scores(query.lower().split())
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
            for idx in top_indices:
                if idx not in seen:
                    seen.add(idx)
                    selected.append(chunks[idx])

    return "\n\n---\n\n".join(selected)


def _build_extract_prompt(lang: str) -> str:
    note = " in Traditional Chinese (繁體中文)" if lang == "zh" else ""
    return _EXTRACT_PROMPT_BASE.replace("{lang_note}", note)


def extract_clauses(
    full_text: str,
    chunks: Optional[list] = None,
    bm25: Optional[BM25Okapi] = None,
    lang: str = "zh",
) -> dict:
    """
    Extract key clauses from a contract.

    If chunks and bm25 are provided, uses BM25 retrieval to find the most
    relevant sections for each clause type — works for documents of any length.
    Falls back to truncating full_text if no index is available.
    """
    if chunks and bm25:
        text_sample = _build_clause_context(chunks, bm25)
    else:
        text_sample = full_text[:12000]

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": _build_extract_prompt(lang).format(text=text_sample)}],
            max_tokens=1500,
            temperature=0,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content.strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])
    except Exception as e:
        error = {"found": False, "summary": f"Extraction error: {e}", "quote": None}
        return {key: error for key in CLAUSE_LABELS}
