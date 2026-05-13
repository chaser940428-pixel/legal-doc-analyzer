"""
Structured clause extraction using Groq LLM.
All 7 clause types are extracted in a single API call to stay within free-tier limits.
"""

import json
import os

from groq import Groq

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

EXTRACT_PROMPT = """\
You are a legal analyst. Read the contract text below and extract the following clauses.

For each clause, return a JSON object with:
- "found": true if the clause exists in the contract, false if not
- "summary": 1-2 sentence plain-language summary (null if not found)
- "quote": the most relevant verbatim excerpt (null if not found)

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

Contract text:
{text}"""


def extract_clauses(full_text: str, max_chars: int = 8000) -> dict:
    text_sample = full_text[:max_chars]
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": EXTRACT_PROMPT.format(text=text_sample)}],
            max_tokens=800,
        )
        raw = response.choices[0].message.content.strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])
    except Exception as e:
        error = {"found": False, "summary": f"Extraction error: {e}", "quote": None}
        return {key: error for key in CLAUSE_LABELS}
