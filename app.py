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

# ── Chinese display labels ──────────────────────────────────────────────────────

ZH_CLAUSE_LABELS = {
    "termination":     "終止條款",
    "payment_terms":   "付款條件",
    "liability":       "責任與賠償",
    "confidentiality": "保密義務",
    "governing_law":   "準據法",
    "ip_ownership":    "智慧財產權歸屬",
    "term_duration":   "合約期間",
}

ZH_RISK_BADGES = {
    "high":   "🔴 高風險",
    "medium": "🟡 中風險",
    "low":    "🟢 低風險",
    "none":   "✅ 無異議",
}

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="法律文件分析工具",
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
        st.error(f"文件處理失敗：{e}")
    return False

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("文件")
    uploaded = st.file_uploader("上傳合約 PDF", type=["pdf"])

    if uploaded:
        if st.button("分析文件", type="primary", use_container_width=True):
            with st.spinner("讀取並建立索引中…"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded.read())
                    tmp_path = tmp.name
                try:
                    success = _index_file(tmp_path, uploaded.name)
                finally:
                    os.unlink(tmp_path)
                if success:
                    st.success(f"已索引 {len(st.session_state['chunks'])} 個段落")
                    st.rerun()

    st.divider()

    if st.button("▶ 載入範例合約", use_container_width=True,
                 help="載入預建的軟體開發服務合約，立即體驗所有功能"):
        if os.path.exists(SAMPLE_PATH):
            with st.spinner("載入範例中…"):
                if _index_file(SAMPLE_PATH, "sample_contract.pdf"):
                    st.rerun()
        else:
            st.error("找不到範例檔案。")

    if "filename" in st.session_state:
        st.info(f"已載入：**{st.session_state['filename']}**")

    st.divider()
    st.caption("Powered by [Groq](https://groq.com) · [GitHub](https://github.com/chaser940428-pixel/legal-doc-analyzer)")

# ── Landing page (no document loaded) ─────────────────────────────────────────

if "chunks" not in st.session_state:
    st.markdown("## ⚖️ 法律文件分析工具")
    st.markdown(
        "上傳任何合約 PDF，在 30 秒內獲得**條款摘要**、"
        "**風險評分**與 **AI 問答**。"
    )
    st.markdown("")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info(
            "**📋 條款自動提取**\n\n"
            "自動辨識 7 大關鍵條款類型：終止、付款、責任、"
            "智慧財產權、保密、準據法、合約期間。"
        )
    with c2:
        st.warning(
            "**⚠️ 風險評估**\n\n"
            "標記高、中、低風險條款，說明具體原因，"
            "並給出整體合約風險評分。"
        )
    with c3:
        st.success(
            "**💬 智能問答**\n\n"
            "以白話文提問——*「逾期付款有什麼後果？」*"
            "——系統僅根據您的文件內容作答。"
        )

    st.markdown("---")
    st.markdown(
        "**開始使用：** 在左側欄上傳 PDF，或點擊 **▶ 載入範例合約** 立即體驗。"
    )
    st.caption(
        "ℹ️ 本工具僅供資訊參考，不構成法律建議。如有法律疑問，請諮詢合格律師。"
    )
    st.stop()

# ── Document loaded ────────────────────────────────────────────────────────────

st.markdown(f"### {st.session_state['filename']}")
tab1, tab2 = st.tabs(["📋 條款摘要與風險", "💬 智能問答"])

# ── Tab 1: Clause extraction + risk assessment ─────────────────────────────────

with tab1:
    if st.session_state.get("clauses") is None:
        st.markdown("文件已建立索引，可開始分析。")
        if st.button("提取關鍵條款", type="primary"):
            with st.spinner("提取條款並評估風險中… （約 20 秒）"):
                clauses = extract_clauses(
                    st.session_state["full_text"],
                    chunks=st.session_state["chunks"],
                    bm25=st.session_state["bm25"],
                )
                risks = assess_risks(clauses)
                st.session_state["clauses"] = clauses
                st.session_state["risks"] = risks

    clauses = st.session_state.get("clauses")
    risks   = st.session_state.get("risks") or {}

    if clauses:
        if risks.get("_error"):
            st.warning(f"風險評估失敗：{risks['_error']}")

        overall = risks.get("overall", {})
        if overall:
            level   = overall.get("level", "low")
            summary = overall.get("summary", "")
            icon  = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(level, "⚪")
            label = {"high": "高風險", "medium": "中風險", "low": "低風險"}.get(level, "")
            banner = f"{icon} **整體風險評估：{label}** — {summary}"
            if level == "high":
                st.error(banner)
            elif level == "medium":
                st.warning(banner)
            else:
                st.success(banner)

        st.divider()

        cols = st.columns(2)
        for i, (key, _) in enumerate(CLAUSE_LABELS.items()):
            result     = clauses.get(key, {})
            risk       = risks.get(key, {})
            risk_level = risk.get("level", "none")
            risk_badge = ZH_RISK_BADGES.get(risk_level, "")
            zh_label   = ZH_CLAUSE_LABELS.get(key, key)

            with cols[i % 2]:
                with st.container(border=True):
                    col_title, col_badge = st.columns([3, 1])
                    with col_title:
                        st.markdown(f"**{zh_label}**")
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
                        st.caption("文件中未找到此條款")

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
            label="⬇ 下載分析報告（PDF）",
            data=st.session_state["report"],
            file_name="legal_analysis_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.caption(
            "ℹ️ AI 生成之分析結果，僅供資訊參考，不構成法律建議。"
        )

# ── Tab 2: Q&A ─────────────────────────────────────────────────────────────────

with tab2:
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if not st.session_state["chat"]:
        st.markdown("**以白話文提問，直接問合約相關問題。**")
        st.markdown("試試範例問題：")
        examples = [
            ("如果逾期付款會怎樣？",       "What happens if I miss a payment? late payment interest penalty"),
            ("合約結束後程式碼歸誰？",       "Who owns the code IP ownership after the contract ends?"),
            ("解除合約需要提前多久通知？",   "How much notice is required to terminate the contract?"),
            ("損害賠償的金額上限是多少？",   "What is the liability cap maximum damages limit?"),
        ]
        ex_cols = st.columns(2)
        for j, (display, query) in enumerate(examples):
            with ex_cols[j % 2]:
                if st.button(display, key=f"ex_{j}", use_container_width=True):
                    with st.spinner("搜尋文件中…"):
                        result = answer(
                            display,
                            st.session_state["chunks"],
                            st.session_state["bm25"],
                            retrieval_query=query,
                        )
                    st.session_state["chat"].append({"role": "user", "content": display})
                    st.session_state["chat"].append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result["sources"],
                    })
                    st.rerun()
        st.markdown("---")

    question = st.chat_input("詢問合約內容…（中英文均可）")

    if question:
        with st.spinner("搜尋文件中…"):
            result = answer(question, st.session_state["chunks"], st.session_state["bm25"])
        st.session_state["chat"].append({"role": "user", "content": question})
        st.session_state["chat"].append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        })
        st.rerun()

    for msg in st.session_state["chat"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("sources"):
                with st.expander("來源段落"):
                    for i, src in enumerate(msg["sources"], 1):
                        st.caption(f"[{i}] {src[:300]}…")
