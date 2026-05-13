"""
Structured clause extraction using Google Gemini.
"""

import json
import os

from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CLAUSE_TYPES = {
    "termination": "What are the conditions or procedures for terminating this agreement?",
    "payment_terms": "What are the payment amounts, schedules, and methods?",
    "liability": "What are the liability limits or indemnification obligations?",
    "confidentiality": "What confidentiality or non-disclosure obligations exist?",
    "governing_law": "Which jurisdiction's law governs this agreement, and where are disputes resolved?",
    "ip_ownership": "Who owns intellectual property created under this agreement?",
    "term_duration": "What is the duration or effective period of this agreement?",
}

EXTRACT_PROMPT = """\
You are a legal analyst. Based on the contract text below, answer this specific question.

Be concise (2-4 sentences). If the contract does not address this, return null.
Return ONLY valid JSON with no markdown: {{"found": true/false, "summary": "...", "quote": "relevant excerpt or null"}}

Question: {question}

Contract text:
{text}"""


def extract_clauses(full_text: str, max_chars: int = 12000) -> dict:
    text_sample = full_text[:max_chars]
    results = {}
    for clause_key, question in CLAUSE_TYPES.items():
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": EXTRACT_PROMPT.format(question=question, text=text_sample)}],
                max_tokens=200,
            )
            raw = response.choices[0].message.content.strip()
            start = raw.find("{")
            end = raw.rfind("}") + 1
            results[clause_key] = json.loads(raw[start:end])
        except Exception as e:
            results[clause_key] = {"found": False, "summary": f"Extraction error: {e}", "quote": None}
    return results


CLAUSE_LABELS = {
    "termination": "Termination",
    "payment_terms": "Payment Terms",
    "liability": "Liability & Indemnification",
    "confidentiality": "Confidentiality",
    "governing_law": "Governing Law",
    "ip_ownership": "IP Ownership",
    "term_duration": "Contract Duration",
}
