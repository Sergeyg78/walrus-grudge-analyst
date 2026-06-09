"""
⚽ FIFA World Cup 2026 — Prediction Tracker & Grudge Agent
Powered by Walrus Testnet Memory + Claude AI Roasts
"""

import streamlit as st
import os
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WC2026 Grudge Agent",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",  # always expanded
)

# ── Imports ────────────────────────────────────────────────────────────────────
from utils.walrus_memory import store_memory, retrieve_memory, get_walrus_explorer_url
from utils.state_manager import (
    empty_state, add_prediction, resolve_prediction, add_hot_take,
    get_pending_predictions, state_to_walrus_payload, walrus_payload_to_state,
)
from utils.roast_engine import get_roast, get_praise, get_debate_response, get_grudge_summary
from utils.wc2026_data import ALL_TEAMS, NOTABLE_MATCHES, TOURNAMENT_INFO

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 40%, #1a0a2e 100%);
    color: #e8eaf6;
  }

  .hero-banner {
    background: linear-gradient(90deg, #1565c0 0%, #6a1b9a 50%, #ad1457 100%);
    border-radius: 16px; padding: 28px 32px; margin-bottom: 24px;
    text-align: center; box-shadow: 0 8px 32px rgba(21,101,192,0.4);
  }
  .hero-banner h1 { font-size: 2.2rem; font-weight: 900; color: #fff; margin: 0; }
  .hero-banner p  { font-size: 1rem; color: rgba(255,255,255,0.8); margin: 6px 0 0; }

  .stat-row { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
  .stat-card {
    flex: 1; min-width: 120px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 12px; padding: 16px; text-align: center;
  }
  .stat-card .val { font-size: 2rem; font-weight: 900; }
  .stat-card .lbl { font-size: 0.75rem; color: rgba(255,255,255,0.55); text-transform: uppercase; letter-spacing: 1px; }
  .green { color: #69f0ae; } .red { color: #ff5252; }
  .yellow { color: #ffd740; } .blue { color: #40c4ff; }

  .section-card {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px; padding: 20px 24px; margin-bottom: 18px;
  }
  .section-title {
    font-size: 1rem; font-weight: 700; color: #90caf9;
    text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 14px;
  }

  .roast-bubble {
    background: linear-gradient(135deg, #b71c1c, #880e4f);
    border-radius: 12px; padding: 16px 20px; border-left: 4px solid #ff5252;
    font-size: 1rem; color: #fff; margin: 12px 0;
    box-shadow: 0 4px 16px rgba(183,28,28,0.3);
  }
  .praise-bubble {
    background: linear-gradient(135deg, #1b5e20, #004d40);
    border-radius: 12px; padding: 16px 20px; border-left: 4px solid #69f0ae;
    font-size: 1rem; color: #fff; margin: 12px 0;
  }
  .debate-bubble {
    background: linear-gradient(135deg, #1a237e, #4a148c);
    border-radius: 12px; padding: 16px 20px; border-left: 4px solid #7986cb;
    font-size: 1rem; color: #fff; margin: 12px 0;
  }

  .pred-row {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px; border-radius: 10px; margin-bottom: 8px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  }
  .badge { padding: 3px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; }
  .badge-pending { background: #f57f17; color: #fff; }
  .badge-correct { background: #2e7d32; color: #fff; }
  .badge-wrong   { background: #c62828; color: #fff; }

  .blob-box {
    background: rgba(0,0,0,0.4); border: 1px solid #37474f;
    border-radius: 8px; padding: 10px 14px;
    font-family: monospace; font-size: 0.8rem; color: #80cbc4; word-break: break-all;
  }

  /* Sidebar always visible */
  [data-testid="stSidebar"] {
    background: rgba(10,14,26,0.97) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
    min-width: 280px !important;
  }
  [data-testid="stSidebarNav"] { display: none; }

  .stTextInput > div > div > input,
  .stSelectbox > div > div,
  .stTextArea textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #e8eaf6 !important; border-radius: 8px !important;
  }
  .stButton > button {
    background: linear-gradient(90deg, #1565c0, #6a1b9a);
    color: #fff; border: none; border-radius: 8px;
    font-weight: 700; padding: 10px 20px; transition: opacity 0.2s;
  }
  .stButton > button:hover { opacity: 0.85; }

  #MainMenu, footer { visibility: hidden; }
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

  /* API key warning banner */
  .api-warning {
    background: linear-gradient(90deg, #e65100, #bf360c);
    border-radius: 10px; padding: 12px 16px; margin-bottom: 16px;
    border-left: 4px solid #ff6d00; color: #fff; font-size: 0.9rem;
  }
</style>
""", unsafe_allow_html=True)


# ── Helper: resolve API key (secrets > session_state > env) ───────────────────
def get_api_key() -> str:
    """
    Priority: Streamlit secrets → session_state → environment variable.
    This ensures the key is always available after st.rerun().
    """
    # 1. Streamlit Cloud secrets (most reliable on cloud)
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    # 2. Session state (user entered in sidebar)
    if st.session_state.get("api_key", ""):
        return st.session_state.api_key
    # 3. Environment variable (local .env)
    return os.environ.get("ANTHROPIC_API_KEY", "")


# ── Session State Init ─────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "state": None,
        "api_key": "",
        "username": "",
        "agent_response": "",
        "last_action": "",
        "setup_done": False,
        "blob_id_display": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session()


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Setup")
    st.markdown("---")

    # ── API Key input ──
    # Pre-fill from secrets if available so user sees it's configured
    secret_key_present = False
    try:
        secret_key_present = bool(st.secrets.get("ANTHROPIC_API_KEY", ""))
    except Exception:
        pass

    if secret_key_present:
        st.success("🔑 API Key loaded from secrets ✅")
    else:
        api_key_input = st.text_input(
            "🔑 Anthropic API Key",
            value=st.session_state.api_key,
            type="password",
            help="Free tier works fine. Get yours at console.anthropic.com",
        )
        # Immediately persist to session state on every render
        if api_key_input.strip():
            st.session_state.api_key = api_key_input.strip()

    # ── Username ──
    username_input = st.text_input(
        "👤 Your Username",
        value=st.session_state.username,
        placeholder="e.g. football_prophet",
    )

    # ── Blob ID loader ──
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
                st.session_state.blob_id_display = ""
                st.session_state.agent_response = (
                    f"Fresh session started for **{st.session_state.username}**. No grudges... yet. 😈"
                )
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
                    st.session_state.blob_id_display = blob_id_input.strip()
                    st.session_state.agent_response = (
                        f"Memory restored for **{st.session_state.username}**! I remember EVERYTHING. 🧠"
                    )
                    st.rerun()
                else:
                    st.error("Could not retrieve blob. Check the ID.")
            else:
                st.error("Paste a blob ID first.")

    st.markdown("---")

    # ── Save to Walrus ──
    if st.session_state.setup_done and st.session_state.state:
        if st.button("💾 Save Memory to Walrus", use_container_width=True):
            with st.spinner("Storing on Walrus testnet..."):
                payload = state_to_walrus_payload(st.session_state.state)
                blob_id = store_memory(payload)
            if blob_id:
                st.session_state.state["blob_id"] = blob_id
                st.session_state.blob_id_display = blob_id
                st.success("✅ Memory saved!")
            else:
                st.error("Walrus save failed. Check testnet status.")

        # Always show last blob ID if available
        display_blob = st.session_state.blob_id_display or st.session_state.state.get("blob_id", "")
        if display_blob:
            st.markdown("**📋 Your Blob ID:**")
            st.code(display_blob, language=None)
            url = get_walrus_explorer_url(display_blob)
            st.markdown(f"[🔍 View on WalrusScan]({url})")

    st.markdown("---")

    # ── API key status indicator (always visible) ──
    resolved_key = get_api_key()
    if resolved_key:
        st.markdown(
            "<div style='font-size:0.78rem; color:#69f0ae'>✅ API Key active</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style='font-size:0.78rem; color:#ff5252'>⚠️ No API Key — enter above</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#546e7a; line-height:1.8'>
    🌊 <b>Walrus Testnet</b><br>
    Memory stored as blobs.<br>
    Blob ID = your memory key.<br><br>
    ⚽ <b>WC2026</b>: Jun 11 – Jul 19, 2026<br>
    🏟️ 48 teams · 104 matches<br>
    📍 USA · Canada · Mexico
    </div>
    """, unsafe_allow_html=True)


# ── Main Area ──────────────────────────────────────────────────────────────────
if not st.session_state.setup_done:
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
          <div style="font-size:0.85rem; color:#78909c">Predictions stored on Walrus testnet as blobs. Load anytime with your Blob ID.</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="section-card" style="text-align:center">
          <div style="font-size:2.5rem">🔥</div>
          <div style="font-weight:700; margin:8px 0; color:#90caf9">AI Roast Engine</div>
          <div style="font-size:0.85rem; color:#78909c">Claude roasts every wrong prediction. Brutally. With receipts from your past failures.</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="section-card" style="text-align:center">
          <div style="font-size:2.5rem">😤</div>
          <div style="font-weight:700; margin:8px 0; color:#90caf9">Grudge System</div>
          <div style="font-size:0.85rem; color:#78909c">Every wrong call is logged. The agent remembers across sessions. Always.</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; padding:24px; color:#546e7a">
      👈 Enter your username and API key in the sidebar, then click <b>🚀 Start / New</b>
    </div>""", unsafe_allow_html=True)

else:
    state = st.session_state.state

    # Resolve API key fresh on every render (fixes rerun loss)
    active_key = get_api_key()

    # ── Show warning if no API key ──
    if not active_key:
        st.markdown("""
        <div class="api-warning">
          ⚠️ <b>No API Key detected.</b> Enter your Anthropic API key in the sidebar to use AI features.
        </div>""", unsafe_allow_html=True)

    # ── Hero ──
    st.markdown(f"""
    <div class="hero-banner">
      <h1>⚽ WC2026 Grudge Agent</h1>
      <p>Welcome back, <b>{state['username']}</b> — I remember everything you've ever gotten wrong.</p>
    </div>""", unsafe_allow_html=True)

    # ── Stats Row ──
    s = state["stats"]
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-card"><div class="val green">{s['correct']}</div><div class="lbl">✅ Correct</div></div>
      <div class="stat-card"><div class="val red">{s['wrong']}</div><div class="lbl">❌ Wrong</div></div>
      <div class="stat-card"><div class="val yellow">{s['pending']}</div><div class="lbl">⏳ Pending</div></div>
      <div class="stat-card"><div class="val blue">{s['win_rate']}</div><div class="lbl">📊 Win Rate</div></div>
      <div class="stat-card"><div class="val" style="color:#ce93d8">{len(state['grudge_log'])}</div><div class="lbl">😤 Grudges</div></div>
    </div>""", unsafe_allow_html=True)

    # ── Agent Response ──
    if st.session_state.agent_response:
        bubble_class = (
            "roast-bubble" if "🔥" in st.session_state.last_action else
            "praise-bubble" if "✅" in st.session_state.last_action else
            "debate-bubble"
        )
        st.markdown(f"""
        <div class="{bubble_class}">
          🤖 <b>Agent:</b> {st.session_state.agent_response}
        </div>""", unsafe_allow_html=True)

    # ── Walrus Memory Panel ──
    with st.expander("🌊 Walrus Memory — Blob ID & Snapshot", expanded=False):
        blob = state.get("blob_id") or st.session_state.blob_id_display
        if blob:
            st.markdown("**Current Blob ID:**")
            st.markdown(f'<div class="blob-box">{blob}</div>', unsafe_allow_html=True)
            st.markdown(f"[🔍 View on WalrusScan]({get_walrus_explorer_url(blob)})")
        else:
            st.info("No blob saved yet. Click **💾 Save Memory to Walrus** in the sidebar.")
        st.markdown("**Memory Snapshot:**")
        st.json(state_to_walrus_payload(state))

    st.markdown("---")

    # ── TABS ──
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Make Prediction", "✅ Resolve Prediction", "💬 Hot Take Debate", "📜 Grudge Report"
    ])

    # ─────────────────────────────────────────────────────────────────
    # Tab 1: Make Prediction
    # ─────────────────────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-title">📝 Make a New Prediction</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
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

    # ─────────────────────────────────────────────────────────────────
    # Tab 2: Resolve Prediction
    # ─────────────────────────────────────────────────────────────────
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
                    if not actual.strip():
                        st.warning("Enter the actual result first.")
                    elif not active_key:
                        st.error("⚠️ Enter your Anthropic API key in the sidebar first!")
                    else:
                        st.session_state.state = resolve_prediction(
                            st.session_state.state, chosen_id, actual.strip(), True
                        )
                        with st.spinner("Generating praise..."):
                            try:
                                response = get_praise(
                                    active_key,
                                    st.session_state.state["username"],
                                    pred_labels[chosen_id],
                                    st.session_state.state["stats"],
                                    st.session_state.state["grudge_log"],
                                )
                            except Exception as e:
                                response = f"Prediction marked correct! (AI response failed: {str(e)[:80]})"
                        st.session_state.agent_response = response
                        st.session_state.last_action = "✅"
                        st.rerun()

            with col2:
                if st.button("❌ Mark Wrong", use_container_width=True):
                    if not actual.strip():
                        st.warning("Enter the actual result first.")
                    elif not active_key:
                        st.error("⚠️ Enter your Anthropic API key in the sidebar first!")
                    else:
                        pred_text = next(p["prediction"] for p in pending if p["id"] == chosen_id)
                        st.session_state.state = resolve_prediction(
                            st.session_state.state, chosen_id, actual.strip(), False
                        )
                        with st.spinner("Preparing roast... 🔥"):
                            try:
                                response = get_roast(
                                    active_key,
                                    st.session_state.state["username"],
                                    pred_text,
                                    actual.strip(),
                                    st.session_state.state["grudge_log"],
                                    st.session_state.state["stats"],
                                )
                            except Exception as e:
                                response = f"Prediction marked wrong! (AI response failed: {str(e)[:80]})"
                        st.session_state.agent_response = response
                        st.session_state.last_action = "🔥"
                        st.rerun()

        # Prediction History
        st.markdown("---")
        st.markdown('<div class="section-title">📋 Prediction History</div>', unsafe_allow_html=True)
        all_preds = st.session_state.state["predictions"]
        if not all_preds:
            st.info("No predictions yet.")
        else:
            for p in reversed(all_preds):
                badge = (
                    '<span class="badge badge-pending">⏳ Pending</span>' if p["status"] == "pending" else
                    '<span class="badge badge-correct">✅ Correct</span>' if p["status"] == "correct" else
                    '<span class="badge badge-wrong">❌ Wrong</span>'
                )
                result_info = f" → <i>{p.get('result', '')}</i>" if p.get("result") else ""
                st.markdown(
                    f'<div class="pred-row">{badge} <b>{p["match"]}</b>: {p["prediction"]}{result_info}'
                    f'<span style="color:#546e7a;font-size:0.75rem;margin-left:auto">{p.get("date","")}</span></div>',
                    unsafe_allow_html=True,
                )

    # ─────────────────────────────────────────────────────────────────
    # Tab 3: Hot Take Debate
    # ─────────────────────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-title">💬 Drop a Hot Take</div>', unsafe_allow_html=True)
        hot_take = st.text_area(
            "Your hot take",
            placeholder="e.g. Mbappe is overrated, France won't make it past the quarters...",
            height=120,
        )

        if st.button("🔥 Submit Hot Take", use_container_width=True):
            if not hot_take.strip():
                st.warning("Type your hot take first!")
            elif not active_key:
                st.error("⚠️ Enter your Anthropic API key in the sidebar first!")
            else:
                # Save take first, then use it for context
                past_takes = list(st.session_state.state["hot_takes"])  # copy before mutation
                st.session_state.state = add_hot_take(st.session_state.state, hot_take.strip())
                with st.spinner("Agent is formulating a counter... 🤔"):
                    try:
                        response = get_debate_response(
                            active_key,
                            st.session_state.state["username"],
                            hot_take.strip(),
                            past_takes,  # pass OLD takes as context, not including current
                        )
                    except Exception as e:
                        response = f"Hot take logged! (AI response failed: {str(e)[:80]})"
                st.session_state.agent_response = response
                st.session_state.last_action = "💬"
                st.rerun()

        if st.session_state.state["hot_takes"]:
            st.markdown("---")
            st.markdown('<div class="section-title">📜 Your Hot Take History</div>', unsafe_allow_html=True)
            for t in reversed(st.session_state.state["hot_takes"]):
                st.markdown(
                    f'<div class="pred-row">💬 <i>"{t["take"]}"</i>'
                    f'<span style="color:#546e7a;font-size:0.75rem;margin-left:auto">{t["date"]}</span></div>',
                    unsafe_allow_html=True,
                )

    # ─────────────────────────────────────────────────────────────────
    # Tab 4: Grudge Report
    # ─────────────────────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-title">😤 The Grudge Report</div>', unsafe_allow_html=True)

        if st.button("💀 Generate Grudge Report", use_container_width=True):
            if not active_key:
                st.error("⚠️ Enter your Anthropic API key in the sidebar first!")
            else:
                with st.spinner("Compiling all your failures... 📋"):
                    try:
                        report = get_grudge_summary(
                            active_key,
                            st.session_state.state["username"],
                            st.session_state.state["grudge_log"],
                            st.session_state.state["stats"],
                        )
                    except Exception as e:
                        report = f"Grudge report failed: {str(e)[:120]}"
                st.session_state.agent_response = report
                st.session_state.last_action = "🔥"
                st.rerun()

        if st.session_state.state["grudge_log"]:
            st.markdown("---")
            st.markdown('<div class="section-title">📋 All Grudges on File</div>', unsafe_allow_html=True)
            for g in reversed(st.session_state.state["grudge_log"]):
                st.markdown(
                    f'<div class="pred-row" style="border-left:3px solid #ff5252">'
                    f'😤 <b>{g["match"]}</b>: predicted "<i>{g["prediction"]}</i>" '
                    f'but "<i>{g["actual"]}</i>" happened'
                    f'<span style="color:#546e7a;font-size:0.75rem;margin-left:auto">{g["date"]}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No grudges yet. Make some wrong predictions first! 😈")

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; font-size:0.8rem; color:#546e7a; padding:8px">
      💡 Always click <b>💾 Save Memory to Walrus</b> after each session — your Blob ID is your memory key!
    </div>""", unsafe_allow_html=True)
