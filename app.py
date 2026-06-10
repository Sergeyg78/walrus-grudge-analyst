"""
⚽ FIFA World Cup 2026 — Grudge Agent v2
Persistent login · Auto-save · Blob chain · Leaderboard · Session Replay
Powered by Walrus Testnet + Claude AI
"""

import os
import streamlit as st

st.set_page_config(
    page_title="WC2026 Grudge Agent",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.walrus_memory import store_memory, retrieve_memory, get_walrus_explorer_url, get_network_name
from utils.state_manager import (
    empty_state, add_prediction, resolve_prediction, add_hot_take,
    get_pending_predictions, get_resolved_predictions,
    state_to_walrus_payload, walrus_payload_to_state,
)
from utils.roast_engine import get_roast, get_praise, get_debate_response, get_grudge_summary
from utils.auth import register_user, login_user, update_user_blob, _hash_credentials, _load_registry
from utils.leaderboard import get_leaderboard, update_leaderboard, get_leaderboard_blob_id
from utils.wc2026_data import ALL_TEAMS, NOTABLE_MATCHES, TOURNAMENT_INFO

# ══════════════════════════════════════════════════════════════════════════════
# CSS — WC2026 Stadium Visual Theme (Full Upgrade)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Oswald:wght@400;600;700&family=Inter:wght@300;400;600;700;900&display=swap');

html,body,[class*="css"]{font-family:'Inter',sans-serif;}

/* ═══════════════════════════════════════════
   BACKGROUND — pitch texture + floodlight glow
   ═══════════════════════════════════════════ */
.stApp {
  background-color: #05080d;
  background-image:
    /* grass stripe bands */
    repeating-linear-gradient(
      180deg,
      transparent 0px, transparent 48px,
      rgba(0,60,20,.18) 48px, rgba(0,60,20,.18) 96px
    ),
    /* diagonal pitch lines */
    repeating-linear-gradient(
      -45deg,
      transparent 0px, transparent 80px,
      rgba(255,255,255,.012) 80px, rgba(255,255,255,.012) 81px
    ),
    /* stadium arc floodlights */
    radial-gradient(ellipse 80% 40% at 50% -5%, rgba(255,240,160,.07) 0%, transparent 70%),
    /* corner glow — USA red */
    radial-gradient(ellipse at 0% 100%, rgba(178,34,52,.18) 0%, transparent 50%),
    /* corner glow — USA blue */
    radial-gradient(ellipse at 100% 0%, rgba(0,40,104,.22) 0%, transparent 50%),
    /* deep base */
    linear-gradient(180deg, #05080d 0%, #060d0a 60%, #080510 100%);
  color: #dde8e2;
  min-height: 100vh;
}

/* ═══════════════════════════════════════════
   HERO — scoreboard + stadium lights
   ═══════════════════════════════════════════ */
.hero {
  position: relative; overflow: hidden;
  background:
    linear-gradient(160deg, #0d1a0e 0%, #001035 45%, #1a000d 100%);
  border-radius: 20px;
  padding: 0;
  margin-bottom: 6px;
  box-shadow:
    0 0 0 1px rgba(255,255,255,.08),
    0 0 40px rgba(0,40,104,.5),
    0 0 80px rgba(0,80,30,.25),
    inset 0 1px 0 rgba(255,255,255,.06);
}

/* stadium arc lights top-left and top-right */
.hero::before {
  content:'';
  position:absolute; inset:0; pointer-events:none;
  background:
    conic-gradient(from 230deg at 5% -10%,  rgba(255,248,200,.14) 0deg, transparent 18deg),
    conic-gradient(from 310deg at 95% -10%,  rgba(255,248,200,.12) 0deg, transparent 18deg),
    conic-gradient(from 200deg at -5% 110%,  rgba(178,34,52,.10)   0deg, transparent 22deg),
    conic-gradient(from 340deg at 105% 110%, rgba(0,40,104,.12)    0deg, transparent 22deg);
}
/* pitch centre-circle echo */
.hero::after {
  content:'';
  position:absolute;
  width:420px; height:420px;
  border:1.5px solid rgba(255,255,255,.04);
  border-radius:50%;
  top:50%; left:50%;
  transform:translate(-50%,-50%);
  pointer-events:none;
}

/* USA tri-stripe bar across very top */
.hero-stripe {
  height: 5px;
  background: linear-gradient(90deg, #b22234 33.3%, #fff 33.3%, #fff 36%, #002868 36%);
  border-radius: 20px 20px 0 0;
}

.hero-inner {
  padding: 28px 32px 26px;
  position: relative; z-index:1;
  text-align: center;
}

/* ball — subtle bounce */
.hero-ball {
  font-size: 3rem; display:block; margin-bottom:8px;
  animation: ballbounce 3s ease-in-out infinite;
  filter: drop-shadow(0 0 18px rgba(255,255,255,.45));
}
@keyframes ballbounce {
  0%,100% { transform: translateY(0) rotate(0deg); }
  30%     { transform: translateY(-8px) rotate(12deg); }
  60%     { transform: translateY(-4px) rotate(-6deg); }
}

/* scoreboard title */
.hero h1 {
  font-family: 'Bebas Neue', 'Oswald', sans-serif;
  font-size: 3rem; font-weight: 400; letter-spacing: 4px;
  color: #fff; margin: 0;
  text-shadow:
    0 0 40px rgba(255,240,160,.5),
    0 0 80px rgba(255,240,160,.2),
    3px 3px 0 rgba(0,0,0,.6);
  text-transform: uppercase;
}

.hero .subtitle {
  font-size: .9rem; color: rgba(255,255,255,.65);
  margin: 8px 0 14px; letter-spacing: .8px;
}

/* pill badges */
.hero-badges { display:flex; gap:8px; justify-content:center; flex-wrap:wrap; }
.hero-badge {
  background: rgba(255,255,255,.1);
  border: 1px solid rgba(255,255,255,.2);
  border-radius: 20px; padding: 4px 14px;
  font-size: .68rem; font-weight: 700; letter-spacing: 1.2px;
  color: #fff; text-transform: uppercase;
  backdrop-filter: blur(6px);
}
.hero-badge.usa  { border-color:rgba(178,34,52,.6);  background:rgba(178,34,52,.2);  }
.hero-badge.wc   { border-color:rgba(255,215,0,.5);  background:rgba(255,215,0,.1);  color:#ffd700; }
.hero-badge.walrus { border-color:rgba(0,188,212,.4);background:rgba(0,188,212,.1);color:#80deea; }

/* ═══════════════════════════════════════════
   LIVE TICKER
   ═══════════════════════════════════════════ */
.ticker-wrap {
  position: relative; overflow:hidden;
  background: linear-gradient(90deg, #b22234 0%, #b22234 8%,
    #002868 8%, #002868 92%, #006633 92%);
  border-radius: 8px; padding: 8px 0; margin-bottom: 16px;
  border: 1px solid rgba(255,255,255,.1);
  box-shadow: 0 2px 12px rgba(0,0,0,.4);
}
.ticker-wrap::before {
  content:'⚽ LIVE';
  position:absolute; left:0; top:0; bottom:0; z-index:2;
  background:#ffd700; color:#000;
  font-size:.68rem; font-weight:900; letter-spacing:1px;
  padding:0 10px; display:flex; align-items:center;
  border-radius:8px 0 0 8px;
}
.ticker-inner {
  display:inline-block; padding-left:calc(100% + 70px);
  animation: ticker 36s linear infinite;
  font-size:.75rem; font-weight:700; color:#fff;
  letter-spacing:1.2px; text-transform:uppercase; white-space:nowrap;
}
@keyframes ticker { 0%{transform:translateX(0)} 100%{transform:translateX(-100%)} }

/* ═══════════════════════════════════════════
   STAT CARDS — scoreboard flip aesthetic
   ═══════════════════════════════════════════ */
.stat-row { display:flex; gap:10px; margin-bottom:20px; flex-wrap:wrap; }
.stat-card {
  flex:1; min-width:100px;
  background: linear-gradient(160deg, rgba(255,255,255,.06), rgba(0,0,0,.2));
  border: 1px solid rgba(255,255,255,.08);
  border-bottom: 3px solid var(--card-accent,#69f0ae);
  border-radius: 10px; padding: 14px 8px; text-align:center;
  box-shadow: 0 4px 20px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.05);
  transition: transform .2s, box-shadow .2s;
  position: relative; overflow:hidden;
}
.stat-card::before {
  content:'';
  position:absolute; left:0; right:0; top:50%; height:1px;
  background: rgba(255,255,255,.04);
}
.stat-card:hover { transform:translateY(-3px); box-shadow:0 8px 28px rgba(0,0,0,.5); }
.stat-card .val {
  font-family:'Bebas Neue','Oswald',sans-serif;
  font-size:2.1rem; font-weight:400; letter-spacing:1px; line-height:1;
}
.stat-card .lbl {
  font-size:.62rem; color:rgba(255,255,255,.4);
  text-transform:uppercase; letter-spacing:1.4px; margin-top:5px;
}
.green  { color:#69f0ae; } .red   { color:#ff5252; }
.yellow { color:#ffd740; } .blue  { color:#40c4ff; }
.purple { color:#ce93d8; } .orange{ color:#ffb74d; }

/* ═══════════════════════════════════════════
   AGENT BUBBLES
   ═══════════════════════════════════════════ */
.roast-bubble {
  position:relative;
  background: linear-gradient(135deg, rgba(183,28,28,.9), rgba(120,0,60,.9));
  border-radius: 14px; padding: 18px 20px 18px 24px;
  border-left: 5px solid #ff1744; color: #fff; margin: 14px 0;
  box-shadow: 0 6px 28px rgba(183,28,28,.4), inset 0 1px 0 rgba(255,255,255,.08);
  font-size: .97rem; line-height: 1.65;
  animation: roast-in .3s ease-out;
}
@keyframes roast-in {
  from { transform: scale(.97) translateY(6px); opacity:.5; }
  to   { transform: scale(1)   translateY(0);   opacity:1; }
}
.roast-bubble .bubble-label {
  font-family:'Oswald',sans-serif; font-size:.65rem;
  letter-spacing:2px; text-transform:uppercase;
  color:rgba(255,255,255,.55); margin-bottom:6px;
  display:flex; align-items:center; gap:6px;
}
.roast-bubble .bubble-label::before {
  content:''; display:inline-block; width:20px; height:2px; background:#ff1744;
}

.praise-bubble {
  background: linear-gradient(135deg, rgba(20,80,30,.9), rgba(0,70,55,.9));
  border-radius: 14px; padding: 18px 20px 18px 24px;
  border-left: 5px solid #00e676; color: #fff; margin: 14px 0;
  box-shadow: 0 6px 28px rgba(0,100,40,.3), inset 0 1px 0 rgba(255,255,255,.08);
  font-size: .97rem; line-height: 1.65;
  animation: roast-in .3s ease-out;
}
.debate-bubble {
  background: linear-gradient(135deg, rgba(20,28,120,.9), rgba(60,10,120,.9));
  border-radius: 14px; padding: 18px 20px 18px 24px;
  border-left: 5px solid #7986cb; color: #fff; margin: 14px 0;
  box-shadow: 0 6px 28px rgba(26,35,126,.3), inset 0 1px 0 rgba(255,255,255,.08);
  font-size: .97rem; line-height: 1.65;
  animation: roast-in .3s ease-out;
}
.info-bubble {
  background: rgba(255,255,255,.04);
  border-radius: 14px; padding: 18px 20px 18px 24px;
  border-left: 5px solid #40c4ff; color: #dde8e2; margin: 14px 0;
  font-size: .97rem; line-height: 1.65;
}
.bubble-agent-tag {
  font-size:.72rem; font-weight:700; letter-spacing:1.5px;
  text-transform:uppercase; opacity:.6; margin-right:6px;
}

/* ═══════════════════════════════════════════
   PREDICTION ROWS
   ═══════════════════════════════════════════ */
.pred-row {
  display:flex; align-items:center; gap:9px;
  padding:11px 15px; border-radius:10px; margin-bottom:7px;
  background: rgba(255,255,255,.03);
  border: 1px solid rgba(255,255,255,.06);
  flex-wrap:wrap; transition: background .15s, transform .1s;
}
.pred-row:hover { background:rgba(255,255,255,.06); transform:translateX(2px); }
.badge {
  padding:3px 11px; border-radius:20px;
  font-size:.65rem; font-weight:800; text-transform:uppercase;
  white-space:nowrap; letter-spacing:.8px; flex-shrink:0;
}
.badge-pending { background:linear-gradient(90deg,#e65100,#f57f17); color:#fff; }
.badge-correct { background:linear-gradient(90deg,#1b5e20,#00c853); color:#fff; }
.badge-wrong   { background:linear-gradient(90deg,#b71c1c,#e53935); color:#fff; }

/* ═══════════════════════════════════════════
   LEADERBOARD
   ═══════════════════════════════════════════ */
.lb-wrap {
  background: linear-gradient(180deg, rgba(0,40,10,.3), rgba(0,0,40,.3));
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 16px; padding: 20px; margin-bottom: 10px;
}
.lb-header {
  font-family:'Bebas Neue','Oswald',sans-serif;
  font-size:1.5rem; letter-spacing:3px;
  color:#ffd700; margin-bottom:16px; text-align:center;
  text-shadow: 0 0 20px rgba(255,215,0,.4);
}
.lb-row {
  display:flex; align-items:center; gap:12px;
  padding:12px 16px; border-radius:11px; margin-bottom:7px;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.07);
  transition: background .15s;
}
.lb-row:hover { background:rgba(255,255,255,.08); }
.lb-row.me {
  border: 1px solid rgba(255,215,0,.5);
  background: rgba(255,215,0,.07);
  box-shadow: 0 0 15px rgba(255,215,0,.1);
}
.lb-rank {
  font-family:'Bebas Neue','Oswald',sans-serif;
  font-size:1.5rem; font-weight:400; min-width:44px; text-align:center;
}
.lb-name { font-weight:700; flex:1; font-size:.95rem; }
.lb-stat { font-size:.78rem; color:#90caf9; }
.lb-winrate {
  font-family:'Oswald',sans-serif; font-size:1rem; font-weight:600;
  color:#ffd740; min-width:52px; text-align:right;
}

/* ═══════════════════════════════════════════
   BLOB BOX
   ═══════════════════════════════════════════ */
.blob-box {
  background: rgba(0,0,0,.6);
  border: 1px solid rgba(0,229,255,.15);
  border-radius: 8px; padding: 10px 14px;
  font-family: 'Courier New', monospace;
  font-size: .75rem; color: #80deea; word-break:break-all;
  box-shadow: inset 0 0 20px rgba(0,229,255,.04), 0 0 10px rgba(0,229,255,.06);
}

/* ═══════════════════════════════════════════
   SECTION HEADINGS
   ═══════════════════════════════════════════ */
.sec-head {
  font-family:'Oswald',sans-serif;
  font-size:1rem; font-weight:600; color:#a5d6a7;
  text-transform:uppercase; letter-spacing:2.5px;
  margin-bottom:14px; padding-bottom:8px;
  border-bottom: 1px solid rgba(165,214,167,.15);
  display:flex; align-items:center; gap:10px;
}
.sec-head::before {
  content:''; display:inline-block; width:3px; height:18px;
  background: linear-gradient(180deg,#69f0ae,#006633);
  border-radius:2px;
}

/* ═══════════════════════════════════════════
   NETWORK BADGE
   ═══════════════════════════════════════════ */
.network-badge {
  display:inline-flex; align-items:center; gap:5px;
  padding:5px 12px; border-radius:20px;
  font-size:.65rem; font-weight:800; text-transform:uppercase; letter-spacing:1.2px;
}
.testnet {
  background:linear-gradient(90deg,#7b1900,#bf360c);
  color:#fff; border:1px solid rgba(255,100,0,.3);
  box-shadow: 0 0 12px rgba(191,54,12,.3);
}
.mainnet {
  background:linear-gradient(90deg,#1b5e20,#2e7d32);
  color:#fff; border:1px solid rgba(0,200,83,.3);
  box-shadow: 0 0 12px rgba(0,200,83,.25);
}

/* ═══════════════════════════════════════════
   AUTOSAVE DOT
   ═══════════════════════════════════════════ */
.autosave-dot {
  display:inline-block; width:7px; height:7px; border-radius:50%;
  background:#69f0ae; margin-right:5px; animation:pulse 2s infinite;
  box-shadow: 0 0 6px #69f0ae;
}
@keyframes pulse { 0%,100%{opacity:1; transform:scale(1);} 50%{opacity:.25; transform:scale(.8);} }

/* ═══════════════════════════════════════════
   SIDEBAR
   ═══════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #04080a 0%, #050a06 50%, #06080d 100%) !important;
  border-right: 1px solid rgba(165,214,167,.08) !important;
  min-width: 272px !important;
}

/* ═══════════════════════════════════════════
   INPUTS
   ═══════════════════════════════════════════ */
.stTextInput>div>div>input,
.stSelectbox>div>div,
.stTextArea textarea {
  background: rgba(255,255,255,.04) !important;
  border: 1px solid rgba(255,255,255,.12) !important;
  color: #dde8e2 !important; border-radius: 9px !important;
  transition: border-color .2s, box-shadow .2s;
}
.stTextInput>div>div>input:focus,
.stTextArea textarea:focus {
  border-color: rgba(105,240,174,.4) !important;
  box-shadow: 0 0 0 3px rgba(105,240,174,.08) !important;
}

/* ═══════════════════════════════════════════
   BUTTONS — USA flag gradient
   ═══════════════════════════════════════════ */
.stButton>button {
  background: linear-gradient(135deg, #006633 0%, #001f5e 50%, #8b0000 100%);
  color: #fff; border: 1px solid rgba(255,255,255,.12);
  border-radius: 9px; font-family:'Oswald',sans-serif;
  font-weight:600; letter-spacing:1.5px; text-transform:uppercase;
  padding: 10px 22px; transition: all .2s;
  box-shadow: 0 4px 16px rgba(0,0,0,.4);
}
.stButton>button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,.5), 0 0 20px rgba(105,240,174,.1);
  border-color: rgba(105,240,174,.3);
}
.stButton>button:active { transform:translateY(0); }

/* ═══════════════════════════════════════════
   TABS
   ═══════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(0,0,0,.2) !important;
  border: 1px solid rgba(255,255,255,.06) !important;
  border-radius: 10px; padding: 4px; gap: 2px;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 7px !important;
  font-family:'Oswald',sans-serif !important;
  font-weight:600 !important; font-size:.78rem !important;
  letter-spacing:1px !important; text-transform:uppercase !important;
  transition: background .2s !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, #006633, #001a4d) !important;
  color: #fff !important;
  box-shadow: 0 2px 10px rgba(0,0,0,.4) !important;
}

/* ═══════════════════════════════════════════
   LANDING FEATURE CARDS
   ═══════════════════════════════════════════ */
.feat-card {
  position: relative; overflow:hidden;
  background: linear-gradient(160deg, rgba(255,255,255,.05), rgba(0,0,0,.15));
  border: 1px solid rgba(255,255,255,.07);
  border-radius: 16px; padding: 26px 20px; text-align:center;
  transition: transform .25s, box-shadow .25s;
  min-height: 200px;
}
.feat-card::after {
  content:''; position:absolute; bottom:0; left:0; right:0; height:3px;
  background: var(--accent-grad, linear-gradient(90deg,#006633,#69f0ae));
  border-radius:0 0 16px 16px;
}
.feat-card:hover {
  transform:translateY(-5px);
  box-shadow:0 12px 36px rgba(0,0,0,.5), 0 0 0 1px rgba(255,255,255,.08);
}
.feat-icon { font-size:2.6rem; display:block; margin-bottom:12px; }
.feat-title {
  font-family:'Oswald',sans-serif; font-size:1rem; font-weight:600;
  color:#a5d6a7; margin-bottom:10px; text-transform:uppercase; letter-spacing:1.5px;
}
.feat-desc { font-size:.8rem; color:#607d8b; line-height:1.6; }

/* ═══════════════════════════════════════════
   MISC
   ═══════════════════════════════════════════ */
#MainMenu,footer { visibility:hidden; }
.block-container { padding-top:1.2rem; padding-bottom:2rem; }

/* horizontal rule */
hr { border-color: rgba(255,255,255,.06) !important; }

/* expander */
.streamlit-expanderHeader {
  font-family:'Oswald',sans-serif !important;
  letter-spacing:1px; font-size:.82rem !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════
def get_api_key() -> str:
    try:
        k = st.secrets.get("ANTHROPIC_API_KEY", "")
        if k: return k
    except Exception:
        pass
    if st.session_state.get("api_key", ""):
        return st.session_state.api_key
    return os.environ.get("ANTHROPIC_API_KEY", "")


def auto_save() -> str | None:
    """Save current state to Walrus and update user registry. Returns blob_id."""
    if not st.session_state.get("logged_in"):
        return None
    payload = state_to_walrus_payload(st.session_state.state)
    blob_id = store_memory(payload)
    if blob_id:
        st.session_state.state["blob_id"] = blob_id
        chain = st.session_state.state.get("blob_chain", [])
        if blob_id not in chain:
            chain.append(blob_id)
        st.session_state.state["blob_chain"] = chain[-20:]
        # Update registry
        update_user_blob(
            st.session_state.username,
            st.session_state.pin,
            blob_id,
        )
        # Update leaderboard
        update_leaderboard(
            st.session_state.username,
            st.session_state.state["stats"],
        )
        st.session_state.last_blob_id = blob_id
    return blob_id


def rank_emoji(i: int) -> str:
    return ["🥇","🥈","🥉"][i] if i < 3 else f"#{i+1}"


# ══════════════════════════════════════════════════════════════════════════════
# Session init
# ══════════════════════════════════════════════════════════════════════════════
DEFAULTS = {
    "logged_in":      False,
    "username":       "",
    "pin":            "",
    "api_key":        "",
    "state":          None,
    "agent_response": "",
    "last_action":    "",
    "last_blob_id":   "",
    "auth_mode":      "login",   # "login" | "register"
    "active_tab":     0,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    net = get_network_name()
    badge_cls = "testnet" if net == "TESTNET" else "mainnet"
    st.markdown(
        f'<span class="network-badge {badge_cls}">🌐 Walrus {net}</span>',
        unsafe_allow_html=True,
    )
    st.markdown("## ⚽ WC2026 Grudge Agent")
    st.markdown("---")

    if not st.session_state.logged_in:
        # ── Auth panel ──
        tabs = st.tabs(["🔑 Login", "📝 Register"])

        with tabs[0]:
            lu = st.text_input("Username", key="login_u", placeholder="your_username")
            lp = st.text_input("4-digit PIN", key="login_p", type="password", max_chars=4)
            if st.button("Login →", use_container_width=True, key="btn_login"):
                if lu.strip() and lp.strip():
                    with st.spinner("Loading your memory from Walrus..."):
                        ok, msg, payload = login_user(lu.strip(), lp.strip())
                    if ok:
                        st.session_state.state = walrus_payload_to_state(payload)
                        st.session_state.state["blob_id"] = msg
                        st.session_state.state["blob_chain"] = payload.get("blob_chain", [msg])
                        st.session_state.username   = lu.strip()
                        st.session_state.pin        = lp.strip()
                        st.session_state.logged_in  = True
                        st.session_state.last_blob_id = msg
                        st.session_state.agent_response = (
                            f"Welcome back **{lu.strip()}**! I remember EVERYTHING. 🧠"
                        )
                        st.session_state.last_action = "💬"
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Fill in both fields.")

        with tabs[1]:
            ru = st.text_input("Choose username", key="reg_u", placeholder="football_prophet")
            rp = st.text_input("Choose 4-digit PIN", key="reg_p", type="password", max_chars=4)
            rp2 = st.text_input("Confirm PIN", key="reg_p2", type="password", max_chars=4)
            if st.button("Create Account →", use_container_width=True, key="btn_reg"):
                if not (ru.strip() and rp.strip() and rp2.strip()):
                    st.warning("Fill in all fields.")
                elif rp != rp2:
                    st.error("PINs don't match.")
                else:
                    with st.spinner("Creating your account on Walrus..."):
                        ok, result = register_user(ru.strip(), rp.strip())
                    if ok:
                        st.success(f"Account created! Login now.")
                    else:
                        st.error(result)

    else:
        # ── Logged-in panel ──
        st.markdown(f"👤 **{st.session_state.username}**")
        s = st.session_state.state["stats"]
        st.markdown(
            f"✅ {s['correct']} correct · ❌ {s['wrong']} wrong · 📊 {s['win_rate']}",
        )
        st.markdown("---")

        # API Key
        secret_set = False
        try:
            secret_set = bool(st.secrets.get("ANTHROPIC_API_KEY", ""))
        except Exception:
            pass

        if secret_set:
            st.success("🔑 API Key from secrets ✅")
        else:
            ak = st.text_input("🔑 Anthropic API Key", type="password",
                               value=st.session_state.api_key,
                               help="Free tier works fine")
            if ak.strip():
                st.session_state.api_key = ak.strip()

        st.markdown("---")

        # Manual save
        if st.button("💾 Save to Walrus", use_container_width=True):
            with st.spinner("Saving..."):
                bid = auto_save()
            if bid:
                st.success("✅ Saved!")
            else:
                st.error("Save failed. Walrus testnet may be down.")

        # Show last blob ID
        if st.session_state.last_blob_id:
            st.markdown("**Last Blob ID:**")
            st.code(st.session_state.last_blob_id, language=None)
            st.markdown(
                f"[🔍 WalrusScan]({get_walrus_explorer_url(st.session_state.last_blob_id)})"
            )

        st.markdown("---")

        # API status
        active_key = get_api_key()
        if active_key:
            st.markdown(
                '<span class="autosave-dot"></span><span style="font-size:.78rem;color:#69f0ae">AI ready</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span style="font-size:.78rem;color:#ff5252">⚠️ No API key</span>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for k in DEFAULTS:
                st.session_state[k] = DEFAULTS[k]
            st.rerun()

        st.markdown("""
        <div style='font-size:.72rem;color:#546e7a;line-height:1.8;margin-top:8px'>
        🔗 Blob chain preserves all history.<br>
        Auto-saves after every action.<br><br>
        ⚽ WC2026: Jun 11–Jul 19, 2026<br>
        🏟️ 48 teams · 104 matches<br>
        📍 USA · Canada · Mexico
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — Not logged in → Landing
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("""
    <div class="hero">
      <div class="hero-stripe"></div>
      <div class="hero-inner">
        <span class="hero-ball">⚽</span>
        <h1>WC2026 Grudge Agent</h1>
        <div class="subtitle">Predict · Get Roasted · Hold Grudges · Never Forget</div>
        <div class="hero-badges">
          <span class="hero-badge usa">🇺🇸 USA 2026</span>
          <span class="hero-badge wc">⚽ 48 Teams · 104 Matches</span>
          <span class="hero-badge walrus">🌊 Walrus Memory</span>
          <span class="hero-badge" style="border-color:rgba(255,100,50,.5);background:rgba(255,80,30,.15);color:#ffab91">🔥 AI Roast Engine</span>
        </div>
      </div>
    </div>

    <div class="ticker-wrap">
      <div class="ticker-inner">
        ⚽ WC2026 kicks off June 11, 2026 &nbsp;·&nbsp;
        🏟️ MetLife Stadium hosts the Final &nbsp;·&nbsp;
        🇺🇸 USA · 🇨🇦 Canada · 🇲🇽 Mexico co-hosting &nbsp;·&nbsp;
        🏆 48 teams competing for glory &nbsp;·&nbsp;
        🔥 Make your predictions — get roasted if you're wrong &nbsp;·&nbsp;
        😤 The agent never forgets &nbsp;·&nbsp;
        🧠 Powered by Walrus persistent memory &nbsp;·&nbsp;
        ⚡ Login to start predicting &nbsp;·&nbsp;
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    feat_data = [
        ("🧠", "Persistent Memory",  "rgba(0,188,212,.6)",  "linear-gradient(90deg,#006064,#00bcd4)",
         "Login with username + PIN. Every action auto-saves to Walrus. No data loss on refresh, ever."),
        ("🔥", "AI Roast Engine",    "rgba(244,67,54,.6)",   "linear-gradient(90deg,#b71c1c,#ff5722)",
         "Claude brutally roasts every wrong call — with full receipts from your past failures."),
        ("😤", "Grudge System",      "rgba(156,39,176,.6)",  "linear-gradient(90deg,#4a148c,#9c27b0)",
         "Wrong predictions logged in a blob chain forever. The agent brings them up. Always."),
    ]
    for col, (icon, title, border, grad, desc) in zip([c1, c2, c3], feat_data):
        with col:
            st.markdown(f"""
            <div class="feat-card" style="--accent-grad:{grad}">
              <span class="feat-icon">{icon}</span>
              <div class="feat-title">{title}</div>
              <div class="feat-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)

    c4, c5 = st.columns(2)
    with c4:
        st.markdown("""
        <div class="feat-card" style="--accent-grad:linear-gradient(90deg,#f57f17,#ffd740)">
          <span class="feat-icon">🏆</span>
          <div class="feat-title">Public Leaderboard</div>
          <div class="feat-desc">See who's the best predictor across all users. Rankings updated live on Walrus after every resolution.</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        st.markdown("""
        <div class="feat-card" style="--accent-grad:linear-gradient(90deg,#1565c0,#40c4ff)">
          <span class="feat-icon">📖</span>
          <div class="feat-title">Session Replay</div>
          <div class="feat-desc">Full timestamped history — every prediction, roast, hot take and grudge — pulled from your Walrus blob chain.</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:28px 0 8px;color:#37474f;font-size:.85rem;letter-spacing:.5px">
      👈 Register or Login in the sidebar to begin your prediction journey
    </div>""", unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — Logged in
# ══════════════════════════════════════════════════════════════════════════════
state      = st.session_state.state
active_key = get_api_key()

# Hero
st.markdown(f"""
<div class="hero">
  <div class="hero-stripe"></div>
  <div class="hero-inner">
    <span class="hero-ball">⚽</span>
    <h1>WC2026 Grudge Agent</h1>
    <div class="subtitle">Welcome back, <b style="color:#ffd700">{state['username']}</b> — I remember everything you've ever gotten wrong 😤</div>
    <div class="hero-badges">
      <span class="hero-badge usa">🇺🇸 USA 2026</span>
      <span class="hero-badge wc">Jun 11 – Jul 19, 2026</span>
      <span class="hero-badge walrus">🌊 Memory Active</span>
    </div>
  </div>
</div>

<div class="ticker-wrap">
  <div class="ticker-inner">
    ⚽ WC2026 kicks off June 11, 2026 &nbsp;·&nbsp;
    🏟️ MetLife Stadium Final &nbsp;·&nbsp;
    🇺🇸 USA · 🇨🇦 Canada · 🇲🇽 Mexico hosting &nbsp;·&nbsp;
    🔥 Every wrong prediction is logged &nbsp;·&nbsp;
    😤 Grudges held forever &nbsp;·&nbsp;
    🧠 Walrus blob chain active &nbsp;·&nbsp;
    ⚡ {state['username']} — make your predictions count &nbsp;·&nbsp;
    🏆 Check the leaderboard &nbsp;·&nbsp;
  </div>
</div>
""", unsafe_allow_html=True)

# Stats
s = state["stats"]
st.markdown(f"""
<div class="stat-row">
  <div class="stat-card"><div class="val green">{s['correct']}</div><div class="lbl">✅ Correct</div></div>
  <div class="stat-card"><div class="val red">{s['wrong']}</div><div class="lbl">❌ Wrong</div></div>
  <div class="stat-card"><div class="val yellow">{s['pending']}</div><div class="lbl">⏳ Pending</div></div>
  <div class="stat-card"><div class="val blue">{s['win_rate']}</div><div class="lbl">📊 Win Rate</div></div>
  <div class="stat-card"><div class="val purple">{len(state['grudge_log'])}</div><div class="lbl">😤 Grudges</div></div>
  <div class="stat-card"><div class="val" style="color:#ffb74d">{len(state['hot_takes'])}</div><div class="lbl">🔥 Hot Takes</div></div>
</div>""", unsafe_allow_html=True)

# Agent response
if st.session_state.agent_response:
    bc = ("roast-bubble"  if "🔥" in st.session_state.last_action else
          "praise-bubble" if "✅" in st.session_state.last_action else
          "debate-bubble" if "💬" in st.session_state.last_action else
          "info-bubble")
    st.markdown(
        f'<div class="{bc}">🤖 <b>Agent:</b> {st.session_state.agent_response}</div>',
        unsafe_allow_html=True,
    )

# Auto-save indicator
if st.session_state.last_blob_id:
    st.markdown(
        f'<div style="font-size:.75rem;color:#546e7a;margin-bottom:8px">'
        f'<span class="autosave-dot"></span>Auto-saved · '
        f'<a href="{get_walrus_explorer_url(st.session_state.last_blob_id)}" '
        f'target="_blank" style="color:#40c4ff">View blob ↗</a></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 Predict", "✅ Resolve", "💬 Hot Takes", "📜 Grudge Report",
    "🏆 Leaderboard", "📖 My History",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Make Prediction
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-title" style="color:#90caf9;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:14px">📝 New Prediction</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        match_sel = st.selectbox("🏟️ Match / Event", ["Custom..."] + NOTABLE_MATCHES)
        match_input = (
            st.text_input("Enter match name", placeholder="e.g. Brazil vs Argentina")
            if match_sel == "Custom..." else match_sel
        )
    with c2:
        pred_text = st.text_area("🔮 Your Prediction",
            placeholder="e.g. Brazil wins 2-1, Vinicius Jr scores", height=120)

    if st.button("📌 Submit Prediction", use_container_width=True, key="btn_predict"):
        if match_input and pred_text.strip():
            st.session_state.state = add_prediction(state, match_input, pred_text.strip())
            st.session_state.agent_response = f'Logged: "{pred_text.strip()}" — let\'s see how this ages. ⏳'
            st.session_state.last_action = "💬"
            with st.spinner("Auto-saving to Walrus..."):
                auto_save()
            st.rerun()
        else:
            st.warning("Fill in both fields.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Resolve
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div style="color:#90caf9;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:14px">✅ Resolve a Prediction</div>', unsafe_allow_html=True)
    pending = get_pending_predictions(st.session_state.state)

    if not pending:
        st.info("No pending predictions. Head to 📝 Predict first!")
    else:
        plabels = {p["id"]: f"#{p['id']} | {p['match']} — {p['prediction']}" for p in pending}
        chosen  = st.selectbox("Pick prediction", list(plabels.keys()), format_func=lambda x: plabels[x])
        actual  = st.text_input("⚡ What actually happened?", placeholder="e.g. Argentina won 3-0")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Mark Correct", use_container_width=True):
                if not actual.strip():
                    st.warning("Enter the actual result.")
                elif not active_key:
                    st.error("⚠️ Add your API key in the sidebar.")
                else:
                    st.session_state.state = resolve_prediction(st.session_state.state, chosen, actual.strip(), True)
                    with st.spinner("Generating praise..."):
                        try:
                            resp = get_praise(active_key, state["username"], plabels[chosen],
                                              st.session_state.state["stats"], st.session_state.state["grudge_log"])
                        except Exception as e:
                            resp = f"Marked correct! (AI unavailable: {str(e)[:60]})"
                    st.session_state.agent_response = resp
                    st.session_state.last_action = "✅"
                    with st.spinner("Auto-saving..."):
                        auto_save()
                    st.rerun()
        with c2:
            if st.button("❌ Mark Wrong", use_container_width=True):
                if not actual.strip():
                    st.warning("Enter the actual result.")
                elif not active_key:
                    st.error("⚠️ Add your API key in the sidebar.")
                else:
                    pred_text_orig = next(p["prediction"] for p in pending if p["id"] == chosen)
                    st.session_state.state = resolve_prediction(st.session_state.state, chosen, actual.strip(), False)
                    with st.spinner("Preparing roast... 🔥"):
                        try:
                            resp = get_roast(active_key, state["username"], pred_text_orig, actual.strip(),
                                             st.session_state.state["grudge_log"], st.session_state.state["stats"])
                        except Exception as e:
                            resp = f"Marked wrong! (AI unavailable: {str(e)[:60]})"
                    st.session_state.agent_response = resp
                    st.session_state.last_action = "🔥"
                    with st.spinner("Auto-saving..."):
                        auto_save()
                    st.rerun()

    # History
    st.markdown("---")
    st.markdown('<div style="color:#90caf9;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px">📋 Prediction History</div>', unsafe_allow_html=True)
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
            res = f" → <i>{p.get('result','')}</i>" if p.get("result") else ""
            st.markdown(
                f'<div class="pred-row">{badge}<b>{p["match"]}</b>: {p["prediction"]}{res}'
                f'<span style="color:#546e7a;font-size:.72rem;margin-left:auto">{p.get("date","")}</span></div>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Hot Takes
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div style="color:#90caf9;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:14px">💬 Drop a Hot Take</div>', unsafe_allow_html=True)
    hot_take = st.text_area("Your hot take",
        placeholder="e.g. Mbappe is overrated, France won't make it past the quarters...",
        height=120)

    if st.button("🔥 Submit Hot Take", use_container_width=True):
        if not hot_take.strip():
            st.warning("Type your hot take first!")
        elif not active_key:
            st.error("⚠️ Add your API key in the sidebar.")
        else:
            past = list(st.session_state.state["hot_takes"])
            st.session_state.state = add_hot_take(st.session_state.state, hot_take.strip())
            with st.spinner("Agent formulating counter... 🤔"):
                try:
                    resp = get_debate_response(active_key, state["username"], hot_take.strip(), past)
                except Exception as e:
                    resp = f"Hot take logged! (AI unavailable: {str(e)[:60]})"
            st.session_state.agent_response = resp
            st.session_state.last_action = "💬"
            with st.spinner("Auto-saving..."):
                auto_save()
            st.rerun()

    if st.session_state.state["hot_takes"]:
        st.markdown("---")
        st.markdown('<div style="color:#90caf9;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px">📜 Hot Take History</div>', unsafe_allow_html=True)
        for t in reversed(st.session_state.state["hot_takes"]):
            st.markdown(
                f'<div class="pred-row">💬 <i>"{t["take"]}"</i>'
                f'<span style="color:#546e7a;font-size:.72rem;margin-left:auto">{t["date"]}</span></div>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — Grudge Report
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div style="color:#90caf9;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:14px">😤 The Grudge Report</div>', unsafe_allow_html=True)

    if st.button("💀 Generate Full Grudge Report", use_container_width=True):
        if not active_key:
            st.error("⚠️ Add your API key in the sidebar.")
        else:
            with st.spinner("Compiling your failures... 📋"):
                try:
                    report = get_grudge_summary(active_key, state["username"],
                                                st.session_state.state["grudge_log"],
                                                st.session_state.state["stats"])
                except Exception as e:
                    report = f"(AI unavailable: {str(e)[:80]})"
            st.session_state.agent_response = report
            st.session_state.last_action = "🔥"
            st.rerun()

    if st.session_state.state["grudge_log"]:
        st.markdown("---")
        for g in reversed(st.session_state.state["grudge_log"]):
            st.markdown(
                f'<div class="pred-row" style="border-left:3px solid #ff5252">'
                f'😤 <b>{g["match"]}</b>: predicted "<i>{g["prediction"]}</i>" '
                f'but "<i>{g["actual"]}</i>" happened'
                f'<span style="color:#546e7a;font-size:.72rem;margin-left:auto">{g["date"]}</span></div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No grudges yet. Make some wrong predictions first! 😈")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — Leaderboard
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    if st.button("🔄 Refresh Leaderboard", use_container_width=True):
        st.rerun()

    with st.spinner("Fetching leaderboard from Walrus..."):
        entries = get_leaderboard()

    if not entries:
        st.info("No leaderboard data yet. Be the first to make and resolve a prediction!")
    else:
        st.markdown('<div class="lb-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="lb-header">🏆 WORLD CUP PREDICTION RANKINGS</div>', unsafe_allow_html=True)
        for i, e in enumerate(entries):
            is_me = e["username"].lower() == st.session_state.username.lower()
            me_cls = "me" if is_me else ""
            you_tag = "&nbsp;<span style='font-size:.62rem;color:#ffd700;font-weight:800;letter-spacing:1px'>YOU</span>" if is_me else ""
            st.markdown(
                f'<div class="lb-row {me_cls}">'
                f'<span class="lb-rank">{rank_emoji(i)}</span>'
                f'<span class="lb-name">{e["username"]} {you_tag}</span>'
                f'<span class="lb-stat">✅ {e["correct"]} &nbsp;❌ {e["wrong"]}</span>'
                f'<span class="lb-winrate">{e["win_rate"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    lb_blob = get_leaderboard_blob_id()
    if lb_blob:
        st.markdown("---")
        st.markdown('<div class="sec-head">Leaderboard Blob ID</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="blob-box">{lb_blob}</div>', unsafe_allow_html=True)
        st.markdown(f"[🔍 Verify on WalrusScan ↗]({get_walrus_explorer_url(lb_blob)})")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 — My History (Session Replay)
# ─────────────────────────────────────────────────────────────────────────────
with tab6:
    st.markdown('<div style="color:#90caf9;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:14px">📖 Full Session History</div>', unsafe_allow_html=True)

    # Blob chain
    chain = st.session_state.state.get("blob_chain", [])
    if chain:
        with st.expander(f"🔗 Blob Chain ({len(chain)} snapshots)", expanded=False):
            for i, bid in enumerate(reversed(chain)):
                label = "← latest" if i == 0 else ""
                st.markdown(
                    f'<div class="blob-box" style="margin-bottom:6px">#{len(chain)-i} {bid} '
                    f'<a href="{get_walrus_explorer_url(bid)}" target="_blank" '
                    f'style="color:#40c4ff;float:right">view ↗</a> '
                    f'<span style="color:#ffd740">{label}</span></div>',
                    unsafe_allow_html=True,
                )

    # Build unified timeline
    timeline = []
    for p in state["predictions"]:
        timeline.append({"date": p.get("date",""), "type": "prediction",
                          "icon": "📝", "text": f'<b>{p["match"]}</b>: {p["prediction"]}',
                          "badge": p["status"]})
        if p.get("result"):
            icon = "✅" if p["status"] == "correct" else "❌"
            timeline.append({"date": p.get("resolved_date", p.get("date","")),
                              "type": "resolution", "icon": icon,
                              "text": f'Resolved: <b>{p["match"]}</b> → {p["result"]}',
                              "badge": p["status"]})
    for g in state["grudge_log"]:
        timeline.append({"date": g.get("date",""), "type": "grudge",
                          "icon": "😤", "text": f'Grudge: "{g["prediction"]}" proved wrong by "{g["actual"]}"',
                          "badge": "wrong"})
    for t in state["hot_takes"]:
        timeline.append({"date": t.get("date",""), "type": "hottake",
                          "icon": "🔥", "text": f'Hot take: <i>"{t["take"]}"</i>',
                          "badge": "take"})

    timeline.sort(key=lambda x: x["date"], reverse=True)

    if not timeline:
        st.info("No history yet. Start making predictions!")
    else:
        badge_styles = {
            "pending": "background:#f57f17",
            "correct": "background:#2e7d32",
            "wrong":   "background:#c62828",
            "take":    "background:#1a237e",
        }
        for item in timeline:
            bstyle = badge_styles.get(item["badge"], "background:#37474f")
            st.markdown(
                f'<div class="pred-row">'
                f'<span style="font-size:1.2rem">{item["icon"]}</span>'
                f'<span style="{bstyle};color:#fff;padding:2px 8px;border-radius:12px;'
                f'font-size:.68rem;font-weight:700;text-transform:uppercase">{item["type"]}</span>'
                f'<span style="flex:1">{item["text"]}</span>'
                f'<span style="color:#546e7a;font-size:.7rem;white-space:nowrap">{item["date"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Raw memory snapshot
    with st.expander("🧬 Raw Memory Snapshot (Walrus payload)", expanded=False):
        st.json(state_to_walrus_payload(st.session_state.state))

st.markdown("""
<div style="text-align:center;font-size:.75rem;color:#37474f;padding:12px;margin-top:8px">
  ⚽ WC2026 Grudge Agent · Powered by Walrus Testnet · Built for Session 4
</div>""", unsafe_allow_html=True)
