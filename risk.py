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

Risk level guidelines:
- "high": seriously dangerous or one-sided terms. Examples:
    * No liability cap or unlimited damages exposure
    * Immediate termination without notice or cause
    * All IP ownership transferred to one party with no compensation
    * Late payment interest above 12% annually (e.g. 1.5% per month = 18% per year is HIGH risk)
    * Aggressive service suspension clauses
    * Clause is completely missing and its absence creates serious legal exposure
- "medium": terms that could be improved or are somewhat unfavorable. Examples:
    * Late payment interest between 6-12% annually
    * Short notice periods for termination
    * Broad IP assignment language
    * Clause is partially missing or vague
- "low": minor concerns, mostly standard industry terms
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

_RISK_PROMPT_ZH = RISK_PROMPT + "\nProvide all 'reason' and 'summary' values in Traditional Chinese (繁體中文)."


def assess_risks(clauses: dict, lang: str = "zh") -> dict:
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
            messages=[{"role": "user", "content": (RISK_PROMPT if lang == "en" else _RISK_PROMPT_ZH).format(clauses=clause_text)}],
            max_tokens=900,
            temperature=0,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content.strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])
    except Exception as e:
        return {"_error": str(e)}
