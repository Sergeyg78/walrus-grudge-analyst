"""
⚽ FIFA World Cup 2026 — Prediction Tracker & Grudge Agent
Powered by Walrus Testnet Memory + Claude AI Roasts
"""

import streamlit as st
import json
import os
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WC2026 Grudge Agent",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports ────────────────────────────────────────────────────────────────────
from utils.walrus_memory import (
    store_memory,
    retrieve_memory,
    get_walrus_explorer_url,
)
from utils.state_manager import (
    empty_state,
    add_prediction,
    resolve_prediction,
    add_hot_take,
    get_pending_predictions,
    get_resolved_predictions,
    state_to_walrus_payload,
    walrus_payload_to_state,
)
from utils.roast_engine import get_roast, get_praise, get_debate_response, get_grudge_summary
from utils.wc2026_data import ALL_TEAMS, NOTABLE_MATCHES, TOURNAMENT_INFO, WC2026_GROUPS

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Google Font ── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* ── Dark gradient background ── */
  .stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 40%, #1a0a2e 100%);
    color: #e8eaf6;
  }

  /* ── Hero banner ── */
  .hero-banner {
    background: linear-gradient(90deg, #1565c0 0%, #6a1b9a 50%, #ad1457 100%);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(21, 101, 192, 0.4);
  }
  .hero-banner h1 { font-size: 2.2rem; font-weight: 900; color: #fff; margin: 0; }
  .hero-banner p  { font-size: 1rem; color: rgba(255,255,255,0.8); margin: 6px 0 0; }

  /* ── Stat cards ── */
  .stat-row { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
  .stat-card {
    flex: 1; min-width: 120px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    backdrop-filter: blur(8px);
  }
  .stat-card .val { font-size: 2rem; font-weight: 900; }
  .stat-card .lbl { font-size: 0.75rem; color: rgba(255,255,255,0.55); text-transform: uppercase; letter-spacing: 1px; }
  .green  { color: #69f0ae; }
  .red    { color: #ff5252; }
  .yellow { color: #ffd740; }
  .blue   { color: #40c4ff; }

  /* ── Section cards ── */
  .section-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 18px;
    backdrop-filter: blur(6px);
  }
  .section-title {
    font-size: 1rem; font-weight: 700;
    color: #90caf9; text-transform: uppercase;
    letter-spacing: 1.5px; margin-bottom: 14px;
  }

  /* ── Roast bubble ── */
  .roast-bubble {
    background: linear-gradient(135deg, #b71c1c, #880e4f);
    border-radius: 12px; padding: 16px 20px;
    border-left: 4px solid #ff5252;
    font-size: 1rem; color: #fff;
    margin: 12px 0;
    box-shadow: 0 4px 16px rgba(183,28,28,0.3);
  }
  .praise-bubble {
    background: linear-gradient(135deg, #1b5e20, #004d40);
    border-radius: 12px; padding: 16px 20px;
    border-left: 4px solid #69f0ae;
    font-size: 1rem; color: #fff;
    margin: 12px 0;
    box-shadow: 0 4px 16px rgba(27,94,32,0.3);
  }
  .debate-bubble {
    background: linear-gradient(135deg, #1a237e, #4a148c);
    border-radius: 12px; padding: 16px 20px;
    border-left: 4px solid #7986cb;
    font-size: 1rem; color: #fff;
    margin: 12px 0;
    box-shadow: 0 4px 16px rgba(26,35,126,0.3);
  }

  /* ── Prediction rows ── */
  .pred-row {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px; border-radius: 10px;
    margin-bottom: 8px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
  }
  .badge {
    padding: 3px 10px; border-radius: 20px; font-size: 0.72rem;
    font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
  }
  .badge-pending  { background: #f57f17; color: #fff; }
  .badge-correct  { background: #2e7d32; color: #fff; }
  .badge-wrong    { background: #c62828; color: #fff; }

  /* ── Blob ID display ── */
  .blob-box {
    background: rgba(0,0,0,0.4); border: 1px solid #37474f;
    border-radius: 8px; padding: 10px 14px;
    font-family: monospace; font-size: 0.8rem; color: #80cbc4;
    word-break: break-all;
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: rgba(10,14,26,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
  }
  [data-testid="stSidebar"] .stMarkdown { color: #b0bec5; }

  /* ── Inputs & Buttons ── */
  .stTextInput > div > div > input,
  .stSelectbox > div > div,
  .stTextArea textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #e8eaf6 !important;
    border-radius: 8px !important;
  }
  .stButton > button {
    background: linear-gradient(90deg, #1565c0, #6a1b9a);
    color: #fff; border: none; border-radius: 8px;
    font-weight: 700; padding: 10px 20px;
    transition: opacity 0.2s;
  }
  .stButton > button:hover { opacity: 0.85; }

  /* ── Hide Streamlit chrome ── */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)


# ── Session State Init ─────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "state": None,
        "api_key": "",
        "username": "",
        "agent_response": "",
        "last_action": "",
        "setup_done": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session()


# ── Sidebar: Setup ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Setup")
    st.markdown("---")

    api_key_input = st.text_input(
        "🔑 Anthropic API Key",
        value=st.session_state.api_key,
        type="password",
        help="Free tier works fine. Get yours at console.anthropic.com",
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

    username_input = st.text_input(
        "👤 Your Username",
        value=st.session_state.username,
        placeholder="e.g. football_prophet",
    )

    blob_id_input = st.text_input(
        "🔗 Load Existing Blob ID (optional)",
        placeholder="Paste a Walrus blob ID to restore memory",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Start / New", use_container_width=True):
            if username_input.strip():
                st.session_state.username = username_input.strip()
                st.session_state.state = empty_state(st.session_state.username)
                st.session_state.setup_done = True
                st.session_state.agent_response = f"Fresh session started for **{st.session_state.username}**. No grudges... yet. 😈"
                st.rerun()
            else:
                st.error("Enter a username first!")

    with col2:
        if st.button("📥 Load Memory", use_container_width=True):
            if blob_id_input.strip():
                with st.spinner("Fetching from Walrus..."):
                    payload = retrieve_memory(blob_id_input.strip())
                if payload:
                    st.session_state.state = walrus_payload_to_state(payload)
                    st.session_state.state["blob_id"] = blob_id_input.strip()
                    st.session_state.username = st.session_state.state["username"]
                    st.session_state.setup_done = True
                    st.session_state.agent_response = f"Memory restored for **{st.session_state.username}**! I remember EVERYTHING. 🧠"
                    st.rerun()
                else:
                    st.error("Could not retrieve blob. Check the ID.")
            else:
                st.error("Paste a blob ID first.")

    st.markdown("---")

    # Save to Walrus
    if st.session_state.setup_done and st.session_state.state:
        if st.button("💾 Save Memory to Walrus", use_container_width=True):
            with st.spinner("Storing on Walrus testnet..."):
                payload = state_to_walrus_payload(st.session_state.state)
                blob_id = store_memory(payload)
            if blob_id:
                st.session_state.state["blob_id"] = blob_id
                st.success("✅ Saved!")
                st.markdown(f"**Blob ID:**")
                st.code(blob_id, language=None)
                url = get_walrus_explorer_url(blob_id)
                st.markdown(f"[🔍 View on WalrusScan]({url})")
            else:
                st.error("Walrus save failed. Check network / testnet status.")

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#546e7a; line-height:1.6'>
    🌊 <b>Walrus Testnet</b><br>
    Memory stored as blobs.<br>
    Blob IDs = your persistent memory.<br><br>
    ⚽ <b>WC2026</b>: Jun 11 – Jul 19, 2026<br>
    🏟️ 48 teams · 104 matches<br>
    📍 USA · Canada · Mexico
    </div>
    """, unsafe_allow_html=True)


# ── Main Area ──────────────────────────────────────────────────────────────────
if not st.session_state.setup_done:
    # ── Landing Screen ──
    st.markdown("""
    <div class="hero-banner">
      <h1>⚽ WC2026 Grudge Agent</h1>
      <p>A memory-powered prediction tracker that roasts your bad calls & holds grudges — forever.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="section-card" style="text-align:center">
          <div style="font-size:2.5rem">🧠</div>
          <div style="font-weight:700; margin:8px 0; color:#90caf9">Persistent Memory</div>
          <div style="font-size:0.85rem; color:#78909c">Your predictions stored on Walrus testnet as blobs. Load them anytime with your Blob ID.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="section-card" style="text-align:center">
          <div style="font-size:2.5rem">🔥</div>
          <div style="font-weight:700; margin:8px 0; color:#90caf9">AI Roast Engine</div>
          <div style="font-size:0.85rem; color:#78909c">Claude roasts every wrong prediction. Brutally. Specifically. With receipts from your past failures.</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="section-card" style="text-align:center">
          <div style="font-size:2.5rem">😤</div>
          <div style="font-weight:700; margin:8px 0; color:#90caf9">Grudge System</div>
          <div style="font-size:0.85rem; color:#78909c">Every wrong call is logged. The agent remembers across sessions and brings it up. Always.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; padding:20px; color:#546e7a">
      👈 Enter your username and API key in the sidebar to begin
    </div>
    """, unsafe_allow_html=True)

else:
    state = st.session_state.state

    # ── Hero ──
    st.markdown(f"""
    <div class="hero-banner">
      <h1>⚽ WC2026 Grudge Agent</h1>
      <p>Welcome back, <b>{state['username']}</b> — I remember everything you've ever gotten wrong.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats Row ──
    s = state["stats"]
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-card"><div class="val green">{s['correct']}</div><div class="lbl">✅ Correct</div></div>
      <div class="stat-card"><div class="val red">{s['wrong']}</div><div class="lbl">❌ Wrong</div></div>
      <div class="stat-card"><div class="val yellow">{s['pending']}</div><div class="lbl">⏳ Pending</div></div>
      <div class="stat-card"><div class="val blue">{s['win_rate']}</div><div class="lbl">📊 Win Rate</div></div>
      <div class="stat-card"><div class="val" style="color:#ce93d8">{len(state['grudge_log'])}</div><div class="lbl">😤 Grudges</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Agent Response Box ──
    if st.session_state.agent_response:
        bubble_class = "roast-bubble" if "🔥" in st.session_state.last_action else (
            "praise-bubble" if "✅" in st.session_state.last_action else "debate-bubble"
        )
        st.markdown(f"""
        <div class="{bubble_class}">
          🤖 <b>Agent:</b> {st.session_state.agent_response}
        </div>
        """, unsafe_allow_html=True)

    # ── Walrus Memory Panel ──
    with st.expander("🌊 Walrus Memory — Blob ID & History", expanded=False):
        if state.get("blob_id"):
            st.markdown("**Current Blob ID (save your memory!):**")
            st.markdown(f'<div class="blob-box">{state["blob_id"]}</div>', unsafe_allow_html=True)
            url = get_walrus_explorer_url(state["blob_id"])
            st.markdown(f"[🔍 View on WalrusScan]({url})")
        else:
            st.info("No blob saved yet. Click **💾 Save Memory to Walrus** in the sidebar after making predictions.")

        st.markdown("**Memory Snapshot (what's stored):**")
        snapshot = state_to_walrus_payload(state)
        st.json(snapshot)

    st.markdown("---")

    # ── TABS ──
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Make Prediction", "✅ Resolve Prediction", "💬 Hot Take Debate", "📜 Grudge Report"
    ])

    # ── Tab 1: Make Prediction ──
    with tab1:
        st.markdown('<div class="section-title">📝 Make a New Prediction</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            match_options = NOTABLE_MATCHES + [f"{t1} vs {t2}" for t1 in ALL_TEAMS[:10] for t2 in ALL_TEAMS[10:15]]
            match_select = st.selectbox("🏟️ Match / Event", options=["Custom..."] + NOTABLE_MATCHES)
            if match_select == "Custom...":
                match_input = st.text_input("Enter match name", placeholder="e.g. Brazil vs Argentina")
            else:
                match_input = match_select

        with col2:
            prediction_text = st.text_area(
                "🔮 Your Prediction",
                placeholder="e.g. Brazil wins 2-1, Vinicius Jr scores",
                height=120,
            )

        if st.button("📌 Submit Prediction", use_container_width=True):
            if match_input and prediction_text.strip():
                st.session_state.state = add_prediction(state, match_input, prediction_text.strip())
                st.session_state.agent_response = f"Logged. \"{prediction_text.strip()}\" — let's see how this ages. ⏳"
                st.session_state.last_action = "📝"
                st.rerun()
            else:
                st.warning("Fill in both the match and prediction fields.")

    # ── Tab 2: Resolve Prediction ──
    with tab2:
        st.markdown('<div class="section-title">✅ Resolve a Pending Prediction</div>', unsafe_allow_html=True)
        pending = get_pending_predictions(st.session_state.state)

        if not pending:
            st.info("No pending predictions. Make some first! 📝")
        else:
            pred_labels = {p["id"]: f"#{p['id']} | {p['match']} — {p['prediction']}" for p in pending}
            chosen_id = st.selectbox(
                "Select prediction to resolve",
                options=list(pred_labels.keys()),
                format_func=lambda x: pred_labels[x],
            )
            actual = st.text_input("⚡ What actually happened?", placeholder="e.g. Argentina won 3-0")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Mark Correct", use_container_width=True):
                    if actual.strip():
                        if not st.session_state.api_key:
                            st.error("Add your Anthropic API key in the sidebar!")
                        else:
                            st.session_state.state = resolve_prediction(st.session_state.state, chosen_id, actual.strip(), True)
                            with st.spinner("Generating praise..."):
                                response = get_praise(
                                    st.session_state.api_key,
                                    st.session_state.state["username"],
                                    pred_labels[chosen_id],
                                    st.session_state.state["stats"],
                                    st.session_state.state["grudge_log"],
                                )
                            st.session_state.agent_response = response
                            st.session_state.last_action = "✅"
                            st.rerun()
                    else:
                        st.warning("Enter the actual result first.")
            with col2:
                if st.button("❌ Mark Wrong", use_container_width=True):
                    if actual.strip():
                        if not st.session_state.api_key:
                            st.error("Add your Anthropic API key in the sidebar!")
                        else:
                            pred_text = next(p["prediction"] for p in pending if p["id"] == chosen_id)
                            st.session_state.state = resolve_prediction(st.session_state.state, chosen_id, actual.strip(), False)
                            with st.spinner("Preparing roast... 🔥"):
                                response = get_roast(
                                    st.session_state.api_key,
                                    st.session_state.state["username"],
                                    pred_text,
                                    actual.strip(),
                                    st.session_state.state["grudge_log"],
                                    st.session_state.state["stats"],
                                )
                            st.session_state.agent_response = response
                            st.session_state.last_action = "🔥"
                            st.rerun()
                    else:
                        st.warning("Enter the actual result first.")

        # ── All Predictions History ──
        st.markdown("---")
        st.markdown('<div class="section-title">📋 Prediction History</div>', unsafe_allow_html=True)
        all_preds = st.session_state.state["predictions"]
        if not all_preds:
            st.info("No predictions yet.")
        else:
            for p in reversed(all_preds):
                badge = (
                    '<span class="badge badge-pending">⏳ Pending</span>'
                    if p["status"] == "pending"
                    else (
                        '<span class="badge badge-correct">✅ Correct</span>'
                        if p["status"] == "correct"
                        else '<span class="badge badge-wrong">❌ Wrong</span>'
                    )
                )
                result_info = f" → <i>{p.get('result', '')}</i>" if p.get("result") else ""
                st.markdown(
                    f'<div class="pred-row">{badge} <b>{p["match"]}</b>: {p["prediction"]}{result_info} <span style="color:#546e7a;font-size:0.75rem;margin-left:auto">{p.get("date","")}</span></div>',
                    unsafe_allow_html=True,
                )

    # ── Tab 3: Hot Take Debate ──
    with tab3:
        st.markdown('<div class="section-title">💬 Drop a Hot Take</div>', unsafe_allow_html=True)
        hot_take = st.text_area(
            "Your hot take",
            placeholder="e.g. Mbappe is overrated, France won't make it past the quarters...",
            height=120,
        )
        if st.button("🔥 Submit Hot Take", use_container_width=True):
            if hot_take.strip():
                if not st.session_state.api_key:
                    st.error("Add your Anthropic API key in the sidebar!")
                else:
                    st.session_state.state = add_hot_take(st.session_state.state, hot_take.strip())
                    with st.spinner("Agent is formulating a counter... 🤔"):
                        response = get_debate_response(
                            st.session_state.api_key,
                            st.session_state.state["username"],
                            hot_take.strip(),
                            st.session_state.state["hot_takes"][:-1],
                        )
                    st.session_state.agent_response = response
                    st.session_state.last_action = "💬"
                    st.rerun()
            else:
                st.warning("Type your hot take first!")

        # ── Past Hot Takes ──
        if st.session_state.state["hot_takes"]:
            st.markdown("---")
            st.markdown('<div class="section-title">📜 Your Hot Take History</div>', unsafe_allow_html=True)
            for t in reversed(st.session_state.state["hot_takes"]):
                st.markdown(
                    f'<div class="pred-row">💬 <i>"{t["take"]}"</i> <span style="color:#546e7a;font-size:0.75rem;margin-left:auto">{t["date"]}</span></div>',
                    unsafe_allow_html=True,
                )

    # ── Tab 4: Grudge Report ──
    with tab4:
        st.markdown('<div class="section-title">😤 The Grudge Report</div>', unsafe_allow_html=True)
        if st.button("💀 Generate Grudge Report", use_container_width=True):
            if not st.session_state.api_key:
                st.error("Add your Anthropic API key in the sidebar!")
            else:
                with st.spinner("Compiling all your failures... 📋"):
                    report = get_grudge_summary(
                        st.session_state.api_key,
                        st.session_state.state["username"],
                        st.session_state.state["grudge_log"],
                        st.session_state.state["stats"],
                    )
                st.session_state.agent_response = report
                st.session_state.last_action = "🔥"
                st.rerun()

        if st.session_state.state["grudge_log"]:
            st.markdown("---")
            st.markdown('<div class="section-title">📋 All Grudges on File</div>', unsafe_allow_html=True)
            for g in reversed(st.session_state.state["grudge_log"]):
                st.markdown(
                    f'<div class="pred-row" style="border-left:3px solid #ff5252">😤 <b>{g["match"]}</b>: predicted "<i>{g["prediction"]}</i>" but "<i>{g["actual"]}</i>" happened <span style="color:#546e7a;font-size:0.75rem;margin-left:auto">{g["date"]}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No grudges yet. Make some wrong predictions first! 😈")

    # ── Auto-save hint ──
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; font-size:0.8rem; color:#546e7a; padding:8px">
      💡 Remember to <b>💾 Save Memory to Walrus</b> in the sidebar after each session — your Blob ID is your memory key!
    </div>
    """, unsafe_allow_html=True)
