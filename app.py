"""
Streamlit UI for legal-doc-analyzer.
Run: streamlit run app.py
"""

import os
import tempfile

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from analyzer import answer, build_index, extract_text
from extractor import CLAUSE_LABELS, extract_clauses
from risk import RISK_LEVELS, assess_risks
from report import generate_report

# ── Language text ───────────────────────────────────────────────────────────────

T = {
    "zh": {
        "page_title":      "法律文件分析工具",
        "lang_label":      "🌐 語言",
        "sidebar_header":  "文件",
        "upload":          "上傳合約 PDF",
        "analyze_btn":     "分析文件",
        "indexed":         "已索引 {} 個段落",
        "sample_btn":      "▶ 載入範例合約",
        "sample_help":     "載入預建的軟體開發服務合約，立即體驗所有功能",
        "active":          "已載入：**{}**",
        "spin_read":       "讀取並建立索引中…",
        "spin_load":       "載入範例中…",
        "err_process":     "文件處理失敗：{}",
        "landing_title":   "## ⚖️ 法律文件分析工具",
        "landing_sub":     "上傳任何合約 PDF，在 30 秒內獲得**條款摘要**、**風險評分**與 **AI 問答**。",
        "card1":           "**📋 條款自動提取**\n\n自動辨識 7 大關鍵條款類型：終止、付款、責任、智慧財產權、保密、準據法、合約期間。",
        "card2":           "**⚠️ 風險評估**\n\n標記高、中、低風險條款，說明具體原因，並給出整體合約風險評分。",
        "card3":           "**💬 智能問答**\n\n以白話文提問——*「逾期付款有什麼後果？」*——系統僅根據您的文件內容作答。",
        "get_started":     "**開始使用：** 在左側欄上傳 PDF，或點擊 **▶ 載入範例合約** 立即體驗。",
        "disclaimer":      "ℹ️ 本工具僅供資訊參考，不構成法律建議。如有法律疑問，請諮詢合格律師。",
        "tab1":            "📋 條款摘要與風險",
        "tab2":            "💬 智能問答",
        "ready":           "文件已建立索引，可開始分析。",
        "extract_btn":     "提取關鍵條款",
        "spin_extract":    "提取條款並評估風險中… （約 20 秒）",
        "risk_err":        "風險評估失敗：{}",
        "overall_prefix":  "整體風險評估：",
        "risk_high":       "高風險",
        "risk_medium":     "中風險",
        "risk_low":        "低風險",
        "not_found":       "文件中未找到此條款",
        "download_btn":    "⬇ 下載分析報告（PDF）",
        "pdf_note":        "ℹ️ PDF 報告以英文輸出。條款摘要與風險說明維持英文以確保準確性。",
        "disclaimer2":     "ℹ️ AI 生成之分析結果，僅供資訊參考，不構成法律建議。",
        "qa_intro":        "**以白話文提問，直接問合約相關問題。**",
        "qa_try":          "試試範例問題：",
        "sources":         "來源段落",
        "spin_search":     "搜尋文件中…",
        "chat_input":      "詢問合約內容…（中英文均可）",
        "clause_labels": {
            "termination":     "終止條款",
            "payment_terms":   "付款條件",
            "liability":       "責任與賠償",
            "confidentiality": "保密義務",
            "governing_law":   "準據法",
            "ip_ownership":    "智慧財產權歸屬",
            "term_duration":   "合約期間",
        },
        "risk_badges": {
            "high":   "🔴 高風險",
            "medium": "🟡 中風險",
            "low":    "🟢 低風險",
            "none":   "✅ 無異議",
        },
        "examples": [
            ("如果逾期付款會怎樣？",       "What happens if I miss a payment? late payment interest penalty"),
            ("合約結束後程式碼歸誰？",       "Who owns the code IP ownership after the contract ends?"),
            ("解除合約需要提前多久通知？",   "How much notice is required to terminate the contract?"),
            ("損害賠償的金額上限是多少？",   "What is the liability cap maximum damages limit?"),
        ],
    },
    "en": {
        "page_title":      "Legal Document Analyzer",
        "lang_label":      "🌐 Language",
        "sidebar_header":  "Document",
        "upload":          "Upload PDF contract",
        "analyze_btn":     "Analyze document",
        "indexed":         "Indexed {} sections",
        "sample_btn":      "▶ Try sample contract",
        "sample_help":     "Load a pre-built software development agreement to explore the tool",
        "active":          "Active: **{}**",
        "spin_read":       "Reading and indexing document…",
        "spin_load":       "Loading sample…",
        "err_process":     "Failed to process document: {}",
        "landing_title":   "## ⚖️ Legal Document Analyzer",
        "landing_sub":     "Upload any contract PDF and get **clause extraction**, **risk scoring**, and an **AI Q&A interface** in under 30 seconds.",
        "card1":           "**📋 Clause Extraction**\n\nAutomatically identifies 7 key clause types: termination, payment, liability, IP ownership, confidentiality, governing law, and duration.",
        "card2":           "**⚠️ Risk Assessment**\n\nFlags high, medium, and low-risk provisions with specific reasons and an overall contract risk score.",
        "card3":           "**💬 Ask Anything**\n\nAsk questions in plain language — *\"What happens if I miss a payment?\"* — answered using only your document.",
        "get_started":     "**Get started:** upload a PDF in the sidebar, or click **▶ Try sample contract** to explore with a pre-built software development agreement.",
        "disclaimer":      "ℹ️ This tool is for informational purposes only and does not constitute legal advice. Consult a qualified attorney for legal matters.",
        "tab1":            "📋 Key Clauses & Risk",
        "tab2":            "💬 Ask Anything",
        "ready":           "Document indexed and ready.",
        "extract_btn":     "Extract key clauses",
        "spin_extract":    "Extracting clauses and assessing risks… (~20 seconds)",
        "risk_err":        "Risk assessment failed: {}",
        "overall_prefix":  "Overall Risk: ",
        "risk_high":       "High Risk",
        "risk_medium":     "Medium Risk",
        "risk_low":        "Low Risk",
        "not_found":       "Not found in document",
        "download_btn":    "⬇ Download Analysis Report (PDF)",
        "pdf_note":        "",
        "disclaimer2":     "ℹ️ AI-generated analysis for informational purposes only. Not legal advice.",
        "qa_intro":        "**Ask anything about this contract in plain language.**",
        "qa_try":          "Try an example:",
        "sources":         "Source excerpts",
        "spin_search":     "Searching document…",
        "chat_input":      "Ask about this contract…",
        "clause_labels": {
            "termination":     "Termination",
            "payment_terms":   "Payment Terms",
            "liability":       "Liability & Indemnification",
            "confidentiality": "Confidentiality",
            "governing_law":   "Governing Law",
            "ip_ownership":    "IP Ownership",
            "term_duration":   "Contract Duration",
        },
        "risk_badges": {
            "high":   "🔴 High Risk",
            "medium": "🟡 Medium Risk",
            "low":    "🟢 Low Risk",
            "none":   "✅ No Issues",
        },
        "examples": [
            ("What happens if I miss a payment?",        None),
            ("Who owns the code after the contract ends?", None),
            ("How much notice is required to terminate?",  None),
            ("What is the liability cap?",                 None),
        ],
    },
}

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Legal Document Analyzer",
    page_icon="⚖️",
    layout="wide",
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer    {visibility: hidden;}
.block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

SAMPLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_contract.pdf")

# ── Language selector (before everything else) ─────────────────────────────────

if "lang" not in st.session_state:
    st.session_state["lang"] = "zh"

with st.sidebar:
    lang_choice = st.radio(
        "🌐",
        ["中文", "English"],
        index=0 if st.session_state["lang"] == "zh" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    new_lang = "zh" if lang_choice == "中文" else "en"
    if st.session_state["lang"] != new_lang:
        st.session_state.pop("chat", None)
        st.session_state["lang"] = new_lang

lang = st.session_state["lang"]
L = T[lang]

# ── Helper ─────────────────────────────────────────────────────────────────────

def _index_file(path: str, name: str) -> bool:
    try:
        chunks, bm25 = build_index(path)
        full_text = extract_text(path)
        st.session_state.update({
            "chunks":    chunks,
            "bm25":      bm25,
            "full_text": full_text,
            "filename":  name,
            "clauses":   None,
            "risks":     None,
            "chat":      [],
            "report":    None,
        })
        return True
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(L["err_process"].format(e))
    return False

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header(L["sidebar_header"])
    uploaded = st.file_uploader(L["upload"], type=["pdf"])

    if uploaded:
        if st.button(L["analyze_btn"], type="primary", use_container_width=True):
            with st.spinner(L["spin_read"]):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded.read())
                    tmp_path = tmp.name
                try:
                    success = _index_file(tmp_path, uploaded.name)
                finally:
                    os.unlink(tmp_path)
                if success:
                    st.success(L["indexed"].format(len(st.session_state["chunks"])))
                    st.rerun()

    st.divider()

    if st.button(L["sample_btn"], use_container_width=True, help=L["sample_help"]):
        if os.path.exists(SAMPLE_PATH):
            with st.spinner(L["spin_load"]):
                if _index_file(SAMPLE_PATH, "sample_contract.pdf"):
                    st.rerun()
        else:
            st.error("Sample file not found.")

    if "filename" in st.session_state:
        st.info(L["active"].format(st.session_state["filename"]))

    st.divider()
    st.caption("Powered by [Groq](https://groq.com) · [GitHub](https://github.com/chaser940428-pixel/legal-doc-analyzer)")

# ── Landing page ───────────────────────────────────────────────────────────────

if "chunks" not in st.session_state:
    st.markdown(L["landing_title"])
    st.markdown(L["landing_sub"])
    st.markdown("")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info(L["card1"])
    with c2:
        st.warning(L["card2"])
    with c3:
        st.success(L["card3"])

    st.markdown("---")
    st.markdown(L["get_started"])
    st.caption(L["disclaimer"])
    st.stop()

# ── Document loaded ────────────────────────────────────────────────────────────

st.markdown(f"### {st.session_state['filename']}")
tab1, tab2 = st.tabs([L["tab1"], L["tab2"]])

# ── Tab 1 ──────────────────────────────────────────────────────────────────────

with tab1:
    if st.session_state.get("clauses") is None:
        st.markdown(L["ready"])
        if st.button(L["extract_btn"], type="primary"):
            with st.spinner(L["spin_extract"]):
                clauses = extract_clauses(
                    st.session_state["full_text"],
                    chunks=st.session_state["chunks"],
                    bm25=st.session_state["bm25"],
                    lang=lang,
                )
                risks = assess_risks(clauses, lang=lang)
                st.session_state["clauses"] = clauses
                st.session_state["risks"] = risks

    clauses = st.session_state.get("clauses")
    risks   = st.session_state.get("risks") or {}

    if clauses:
        if risks.get("_error"):
            st.warning(L["risk_err"].format(risks["_error"]))

        overall = risks.get("overall", {})
        if overall:
            level   = overall.get("level", "low")
            summary = overall.get("summary", "")
            icon    = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(level, "⚪")
            label   = {"high": L["risk_high"], "medium": L["risk_medium"], "low": L["risk_low"]}.get(level, "")
            banner  = f"{icon} **{L['overall_prefix']}{label}** — {summary}"
            if level == "high":
                st.error(banner)
            elif level == "medium":
                st.warning(banner)
            else:
                st.success(banner)

        st.divider()

        cols = st.columns(2)
        for i, key in enumerate(CLAUSE_LABELS):
            result     = clauses.get(key, {})
            risk       = risks.get(key, {})
            risk_level = risk.get("level", "none")
            risk_badge = L["risk_badges"].get(risk_level, "")
            label      = L["clause_labels"].get(key, key)

            with cols[i % 2]:
                with st.container(border=True):
                    col_title, col_badge = st.columns([3, 1])
                    with col_title:
                        st.markdown(f"**{label}**")
                    with col_badge:
                        st.markdown(
                            f"<div style='text-align:right'>{risk_badge}</div>",
                            unsafe_allow_html=True,
                        )

                    if result.get("found"):
                        st.write(result.get("summary", "—"))
                        if result.get("quote"):
                            st.caption(f"> {result['quote']}")
                    else:
                        st.caption(L["not_found"])

                    if risk.get("reason"):
                        st.caption(f"_{risk['reason']}_")

        st.divider()

        if st.session_state.get("report") is None:
            st.session_state["report"] = generate_report(
                st.session_state.get("filename", "document.pdf"),
                clauses,
                risks,
                CLAUSE_LABELS,
            )
        st.download_button(
            label=L["download_btn"],
            data=st.session_state["report"],
            file_name="legal_analysis_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        if L["pdf_note"]:
            st.caption(L["pdf_note"])
        st.caption(L["disclaimer2"])

# ── Tab 2 ──────────────────────────────────────────────────────────────────────

with tab2:
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if not st.session_state["chat"]:
        st.markdown(L["qa_intro"])
        st.markdown(L["qa_try"])
        ex_cols = st.columns(2)
        for j, (display, query) in enumerate(L["examples"]):
            with ex_cols[j % 2]:
                if st.button(display, key=f"ex_{j}", use_container_width=True):
                    with st.spinner(L["spin_search"]):
                        result = answer(
                            display,
                            st.session_state["chunks"],
                            st.session_state["bm25"],
                            retrieval_query=query,
                            lang=lang,
                        )
                    st.session_state["chat"].append({"role": "user", "content": display})
                    st.session_state["chat"].append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result["sources"],
                    })
                    st.rerun()
        st.markdown("---")

    for msg in st.session_state["chat"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("sources"):
                with st.expander(L["sources"]):
                    for i, src in enumerate(msg["sources"], 1):
                        st.caption(f"[{i}] {src[:300]}…")

    question = st.chat_input(L["chat_input"])

    if question:
        with st.spinner(L["spin_search"]):
            result = answer(question, st.session_state["chunks"], st.session_state["bm25"], lang=lang)
        st.session_state["chat"].append({"role": "user", "content": question})
        st.session_state["chat"].append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        })
        st.rerun()
