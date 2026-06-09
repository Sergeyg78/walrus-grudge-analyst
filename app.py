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
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}

.stApp{background:linear-gradient(135deg,#0a0e1a 0%,#0d1b2a 40%,#1a0a2e 100%);color:#e8eaf6;}

.hero{background:linear-gradient(90deg,#1565c0 0%,#6a1b9a 50%,#ad1457 100%);
  border-radius:16px;padding:28px 32px;margin-bottom:20px;text-align:center;
  box-shadow:0 8px 32px rgba(21,101,192,.4);}
.hero h1{font-size:2.2rem;font-weight:900;color:#fff;margin:0;}
.hero p{font-size:1rem;color:rgba(255,255,255,.8);margin:6px 0 0;}

.stat-row{display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap;}
.stat-card{flex:1;min-width:110px;background:rgba(255,255,255,.06);
  border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:14px;text-align:center;}
.stat-card .val{font-size:1.9rem;font-weight:900;}
.stat-card .lbl{font-size:.72rem;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:1px;}
.green{color:#69f0ae;}.red{color:#ff5252;}.yellow{color:#ffd740;}.blue{color:#40c4ff;}.purple{color:#ce93d8;}

.roast-bubble{background:linear-gradient(135deg,#b71c1c,#880e4f);border-radius:12px;
  padding:16px 20px;border-left:4px solid #ff5252;color:#fff;margin:12px 0;
  box-shadow:0 4px 16px rgba(183,28,28,.3);}
.praise-bubble{background:linear-gradient(135deg,#1b5e20,#004d40);border-radius:12px;
  padding:16px 20px;border-left:4px solid #69f0ae;color:#fff;margin:12px 0;}
.debate-bubble{background:linear-gradient(135deg,#1a237e,#4a148c);border-radius:12px;
  padding:16px 20px;border-left:4px solid #7986cb;color:#fff;margin:12px 0;}
.info-bubble{background:rgba(255,255,255,.05);border-radius:12px;
  padding:16px 20px;border-left:4px solid #40c4ff;color:#e8eaf6;margin:12px 0;}

.pred-row{display:flex;align-items:center;gap:8px;padding:10px 14px;border-radius:10px;
  margin-bottom:7px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);
  flex-wrap:wrap;}
.badge{padding:3px 10px;border-radius:20px;font-size:.7rem;font-weight:700;
  text-transform:uppercase;white-space:nowrap;}
.badge-pending{background:#f57f17;color:#fff;}
.badge-correct{background:#2e7d32;color:#fff;}
.badge-wrong{background:#c62828;color:#fff;}

.blob-box{background:rgba(0,0,0,.4);border:1px solid #37474f;border-radius:8px;
  padding:10px 14px;font-family:monospace;font-size:.78rem;color:#80cbc4;word-break:break-all;}

.lb-row{display:flex;align-items:center;gap:10px;padding:10px 14px;border-radius:10px;
  margin-bottom:6px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);}
.lb-rank{font-size:1.3rem;font-weight:900;min-width:36px;}
.lb-name{font-weight:700;flex:1;}
.lb-stat{font-size:.82rem;color:#90caf9;}

.network-badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:.7rem;
  font-weight:700;text-transform:uppercase;letter-spacing:1px;}
.testnet{background:#e65100;color:#fff;}
.mainnet{background:#2e7d32;color:#fff;}

.autosave-dot{display:inline-block;width:8px;height:8px;border-radius:50%;
  background:#69f0ae;margin-right:6px;animation:pulse 2s infinite;}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:.3;}}

[data-testid="stSidebar"]{background:rgba(10,14,26,.97)!important;
  border-right:1px solid rgba(255,255,255,.08);min-width:270px!important;}
.stTextInput>div>div>input,.stSelectbox>div>div,.stTextArea textarea{
  background:rgba(255,255,255,.06)!important;border:1px solid rgba(255,255,255,.15)!important;
  color:#e8eaf6!important;border-radius:8px!important;}
.stButton>button{background:linear-gradient(90deg,#1565c0,#6a1b9a);color:#fff;
  border:none;border-radius:8px;font-weight:700;padding:10px 20px;transition:opacity .2s;}
.stButton>button:hover{opacity:.85;}
#MainMenu,footer{visibility:hidden;}
.block-container{padding-top:1.4rem;padding-bottom:2rem;}
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
      <h1>⚽ WC2026 Grudge Agent</h1>
      <p>Predict · Get Roasted · Hold Grudges · Never Forget — Powered by Walrus Memory</p>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    cards = [
        ("🧠", "Persistent Memory", "Login with username + PIN. Every action saved to Walrus automatically. No data loss on refresh ever again."),
        ("🔥", "AI Roast Engine", "Claude brutally roasts every wrong call — with full receipts from your past failures going back to session 1."),
        ("😤", "Grudge System", "Wrong predictions are logged forever in a blob chain. The agent brings them up. Always. Across every session."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3], cards):
        with col:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);
              border-radius:14px;padding:20px 24px;text-align:center;height:180px">
              <div style="font-size:2.2rem">{icon}</div>
              <div style="font-weight:700;margin:8px 0;color:#90caf9">{title}</div>
              <div style="font-size:.83rem;color:#78909c">{desc}</div>
            </div>""", unsafe_allow_html=True)

    c4, c5 = st.columns(2)
    with c4:
        st.markdown("""
        <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);
          border-radius:14px;padding:20px 24px;text-align:center">
          <div style="font-size:2.2rem">🏆</div>
          <div style="font-weight:700;margin:8px 0;color:#90caf9">Public Leaderboard</div>
          <div style="font-size:.83rem;color:#78909c">See who's the best predictor across all users. Updated live after every resolution.</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        st.markdown("""
        <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);
          border-radius:14px;padding:20px 24px;text-align:center">
          <div style="font-size:2.2rem">📖</div>
          <div style="font-weight:700;margin:8px 0;color:#90caf9">Full Session Replay</div>
          <div style="font-size:.83rem;color:#78909c">Every prediction, roast, hot take and grudge — timestamped and replayed in order.</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:24px;color:#546e7a">
      👈 Register or Login in the sidebar to begin
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
  <h1>⚽ WC2026 Grudge Agent</h1>
  <p>Welcome back, <b>{state['username']}</b> — I remember everything you've ever gotten wrong. 😤</p>
</div>""", unsafe_allow_html=True)

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
    st.markdown('<div style="color:#90caf9;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:14px">🏆 Public Leaderboard</div>', unsafe_allow_html=True)

    if st.button("🔄 Refresh Leaderboard", use_container_width=True):
        st.rerun()

    with st.spinner("Fetching leaderboard from Walrus..."):
        entries = get_leaderboard()

    if not entries:
        st.info("No leaderboard data yet. Be the first to make and resolve a prediction!")
    else:
        for i, e in enumerate(entries):
            is_me = e["username"].lower() == st.session_state.username.lower()
            highlight = "border:1px solid #ffd740;" if is_me else ""
            total = e["correct"] + e["wrong"]
            st.markdown(
                f'<div class="lb-row" style="{highlight}">'
                f'<span class="lb-rank">{rank_emoji(i)}</span>'
                f'<span class="lb-name">{e["username"]}{"  👈 you" if is_me else ""}</span>'
                f'<span class="lb-stat">✅ {e["correct"]} · ❌ {e["wrong"]} · 📊 {e["win_rate"]}</span>'
                f'<span style="color:#546e7a;font-size:.7rem;margin-left:auto">{e.get("last_updated","")[:10]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    lb_blob = get_leaderboard_blob_id()
    if lb_blob:
        st.markdown("---")
        st.markdown("**Leaderboard Blob ID** (public proof on Walrus):")
        st.markdown(f'<div class="blob-box">{lb_blob}</div>', unsafe_allow_html=True)
        st.markdown(f"[🔍 View on WalrusScan]({get_walrus_explorer_url(lb_blob)})")


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
