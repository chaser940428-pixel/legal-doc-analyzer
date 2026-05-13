"""
Risk assessment for extracted contract clauses.
Uses clause summaries (not full text) to stay well within Groq token limits.
"""

import json
import os

from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

RISK_LEVELS = {
    "high": "🔴 High Risk",
    "medium": "🟡 Medium Risk",
    "low": "🟢 Low Risk",
    "none": "✅ No Issues",
}

RISK_PROMPT = """\
You are a legal risk analyst. Review these contract clause summaries and assess the risk of each.

Guidelines:
- "high": dangerous terms, severely one-sided, missing critical protection (e.g. no liability cap, IP all goes to one party, immediate termination with no notice)
- "medium": terms could be improved, somewhat one-sided, or clause is partially missing
- "low": minor concerns, mostly standard terms
- "none": fair, complete, and balanced

If a clause is marked MISSING, assess whether its absence creates risk.

Clause summaries:
{clauses}

Return ONLY valid JSON, no markdown:
{{
  "termination": {{"level": "high|medium|low|none", "reason": "one sentence"}},
  "payment_terms": {{"level": "high|medium|low|none", "reason": "one sentence"}},
  "liability": {{"level": "high|medium|low|none", "reason": "one sentence"}},
  "confidentiality": {{"level": "high|medium|low|none", "reason": "one sentence"}},
  "governing_law": {{"level": "high|medium|low|none", "reason": "one sentence"}},
  "ip_ownership": {{"level": "high|medium|low|none", "reason": "one sentence"}},
  "term_duration": {{"level": "high|medium|low|none", "reason": "one sentence"}},
  "overall": {{"level": "high|medium|low", "summary": "1-2 sentence overall assessment"}}
}}"""


def assess_risks(clauses: dict) -> dict:
    lines = []
    for key, data in clauses.items():
        if data.get("found"):
            lines.append(f"{key} (present): {data.get('summary', '')}")
        else:
            lines.append(f"{key}: MISSING from contract")
    clause_text = "\n".join(lines)

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": RISK_PROMPT.format(clauses=clause_text)}],
            max_tokens=600,
        )
        raw = response.choices[0].message.content.strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])
    except Exception:
        return {}
