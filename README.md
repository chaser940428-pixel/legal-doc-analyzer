# Legal Document Analyzer

> Upload any contract PDF. Get instant structured clause extraction and plain-language Q&A — grounded in the document itself.

**[Live Demo](https://legal-doc-analyzer-jdmijowrqdsr8jvz4rak6c.streamlit.app)** &nbsp;|&nbsp; Built with Groq + Streamlit &nbsp;|&nbsp; No API key needed to try

---

## Why this exists

Most people sign contracts they don't fully understand. Reading a 20-page service agreement takes an hour — and even then, non-lawyers miss critical clauses about termination, liability, and IP ownership.

General-purpose AI (ChatGPT, Claude) can help, but it's still a manual process: copy the text, paste it in, ask the right questions. If you don't know what to look for, you won't find it.

This tool is built specifically for contracts. Upload a PDF and it automatically surfaces what matters — without you having to know the right questions to ask.

---

## Why not just use ChatGPT?

| | ChatGPT / Claude | Legal Doc Analyzer |
|---|---|---|
| Upload PDF directly | Requires paid plan | Free |
| Knows what to extract | You have to ask | Auto-extracts 7 clause types |
| Cites exact document text | Inconsistent | Every answer includes source quote |
| Built for contract review | General purpose | Purpose-built |
| Ask follow-up questions | Loses context | Persistent session per document |

The core difference: **this tool knows what legal clauses matter before you ask.** It scans the contract and flags them automatically. You get a structured briefing, not a blank chat box.

---

## What it extracts automatically

Without any prompting, the analyzer identifies and summarizes:

- **Termination** — conditions and notice requirements to end the agreement
- **Payment Terms** — amounts, schedules, and late payment consequences
- **Liability & Indemnification** — damage caps and who bears what risk
- **Confidentiality** — what's covered, for how long, and what's excluded
- **Governing Law** — which jurisdiction's law applies and where disputes are resolved
- **IP Ownership** — who owns work created under the agreement
- **Contract Duration** — effective dates, renewal, and expiry

---

## How to use it

1. Open the [live demo](https://chaser940428-pixel-legal-doc-analyzer-app-3msjpf.streamlit.app)
2. Upload any PDF contract in the sidebar (try the included `sample_contract.pdf`)
3. Click **Analyze document**
4. Go to **Key Clauses** tab → click **Extract key clauses**
5. Go to **Ask Anything** tab → ask questions in plain language

No setup, no API key, no account required.

---

## Sample questions to try

```
What are the grounds for immediate termination?
Who is responsible if the deliverable is rejected?
Can the client share this work with third parties?
What happens to IP created during the engagement?
Is there a non-compete clause?
```

---

## How it works

```
PDF upload
    └── pdfplumber extracts full text
            └── text split into 300-word overlapping chunks
                    └── BM25 index built over all chunks
                            └── User question → BM25 retrieves top 2 relevant chunks
                                    └── Groq LLM (llama-3.1-8b-instant) answers from chunks only
```

**RAG (Retrieval-Augmented Generation)** means the LLM only sees the parts of the document relevant to the question — not the whole thing. This keeps answers accurate, fast, and grounded. The model cannot fabricate clauses that aren't there.

---

## Tech stack

| Component | Tool |
|---|---|
| LLM | Groq API — `llama-3.1-8b-instant` (free tier) |
| Retrieval | BM25 via `rank-bm25` (no vector DB needed) |
| PDF parsing | `pdfplumber` |
| UI | Streamlit |
| Clause extraction | Structured JSON prompting over Groq |

---

## Local setup

```bash
git clone https://github.com/chaser940428-pixel/legal-doc-analyzer
cd legal-doc-analyzer
pip install -r requirements.txt
```

Create a `.env` file:
```
GROQ_API_KEY=your_key_here
```

Get a free key at [console.groq.com](https://console.groq.com) — no credit card required.

```bash
streamlit run app.py
```

---

## Extending

To add a new clause type, add one entry to `CLAUSE_TYPES` in `extractor.py`:

```python
"dispute_resolution": "How are disputes between the parties resolved?",
```

No other changes needed. The extraction pipeline picks it up automatically.

---

## Project structure

```
legal-doc-analyzer/
├── app.py              # Streamlit UI — upload, tabs, chat
├── analyzer.py         # RAG pipeline — chunk, index, retrieve, answer
├── extractor.py        # Structured clause extraction with JSON output
├── sample_contract.pdf # Sample service agreement for testing
├── requirements.txt
└── .env.example
```
