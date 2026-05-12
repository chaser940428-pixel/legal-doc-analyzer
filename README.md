# legal-doc-analyzer

Upload any contract or legal document (PDF). Get instant AI-powered clause extraction and a natural language Q&A interface.

Built to demonstrate RAG (Retrieval-Augmented Generation) applied to legal document workflows — the core pattern behind modern LegalTech automation.

## What it does

**Step 1 — Upload**
Drop in any PDF contract. The system extracts and indexes the full text.

**Step 2 — Auto-extract key clauses**
Without any prompting, the AI identifies and summarizes:
- Termination conditions
- Payment terms
- Liability and indemnification
- Confidentiality obligations
- Governing law

**Step 3 — Ask anything**
Type any question in plain language:
- "What happens if either party wants to cancel?"
- "Is there a penalty for late payment?"
- "Who owns the intellectual property?"

The system finds the relevant sections and answers based only on the document — no hallucination.

## Why this matters for LegalTech

Law firms and legal teams spend hours reading contracts to find specific clauses. This demo shows how that process can be reduced to seconds using:
- **RAG pipeline**: retrieve only the relevant sections before answering
- **Structured extraction**: pull standardized fields from any contract format
- **Grounded responses**: answers cite the source text, not AI assumptions

## Tech stack

- `pdfplumber` — PDF text extraction
- `openai` — embeddings (`text-embedding-3-small`) + completion (`gpt-4o-mini`)
- `numpy` — cosine similarity for retrieval (no external vector DB needed)
- `streamlit` — interactive web UI for demo

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/legal-doc-analyzer
cd legal-doc-analyzer
pip install -r requirements.txt
cp .env.example .env
# Add your OPENAI_API_KEY to .env
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

## Project structure

```
legal-doc-analyzer/
├── app.py           # Streamlit UI
├── analyzer.py      # RAG pipeline: chunk, embed, retrieve, answer
├── extractor.py     # Structured clause extraction
├── requirements.txt
└── .env.example
```

## How the RAG pipeline works

```
PDF → extract text → split into chunks (500 words, 50 overlap)
                          ↓
                    embed each chunk (OpenAI)
                          ↓
User question → embed question → cosine similarity → top 3 chunks
                                                          ↓
                                               LLM answers from chunks only
```

This is the same architecture used in enterprise document intelligence products — implemented here in ~150 lines of Python with no framework overhead.

## Extending

To add a new auto-extracted clause type, add one entry to `CLAUSE_TYPES` in `extractor.py`:

```python
CLAUSE_TYPES = {
    ...
    "dispute_resolution": "How are disputes between the parties resolved?",
}
```

No other changes needed.
