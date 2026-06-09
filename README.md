# ⚽ WC2026 Grudge Agent v2

> A memory-powered FIFA World Cup 2026 prediction tracker with **persistent login**, **auto-save**, **blob chain memory**, **public leaderboard**, **session replay**, and **mainnet-ready toggle** — powered by Walrus + Claude AI.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red)
![Walrus](https://img.shields.io/badge/Walrus-Testnet-teal)
![Claude](https://img.shields.io/badge/Claude-Haiku-purple)

---

## ✨ What's New in v2

| Feature | Description |
|---|---|
| 🔐 **Username + PIN Login** | Register once, login forever. Your data always loads back automatically. |
| 🔗 **Blob Chain Memory** | Every save links to the previous blob — full history always recoverable. |
| 💾 **Auto-save** | Every prediction, resolution, and hot take saves to Walrus automatically. No manual saves needed. |
| 🏆 **Public Leaderboard** | All users' win rates on one shared Walrus blob — updated live. |
| 📖 **Session Replay** | Full timestamped history of every action, all in one tab. |
| 🌐 **Mainnet Toggle** | One env var switches from testnet to mainnet: `WALRUS_NETWORK=mainnet` |

---

## 🚀 Step-by-Step: Push Update to GitHub & Redeploy

### Step 1 — Open your Codespace
Go to `https://github.com/Sergeyg78/walrus-grudge-analyst` → click **Code** → **Codespaces** → open your existing codespace.

### Step 2 — Upload the new zip
In the Codespaces file explorer (left sidebar):
- Right-click → **Upload...**
- Select `wc2026-grudge-agent.zip`

### Step 3 — Open the terminal (Ctrl + `)
Run these commands one by one:

```bash
# Unzip
unzip -o wc2026-grudge-agent.zip

# Copy all new files into repo root (overwrites old files)
cp -r wc2026-agent/. .

# Clean up
rm -rf wc2026-grudge-agent.zip wc2026-agent
```

### Step 4 — Verify the new files are there
```bash
ls utils/
# Should show: auth.py  leaderboard.py  roast_engine.py  state_manager.py  walrus_memory.py  wc2026_data.py
```

### Step 5 — Push to GitHub
```bash
git add .
git commit -m "feat: v2 — login, auto-save, blob chain, leaderboard, session replay"
git push
```

### Step 6 — Streamlit Cloud redeploys automatically
- Wait ~60 seconds
- Visit your Streamlit URL — the new version will be live
- **No action needed on Streamlit Cloud itself** — it watches your GitHub repo

### Step 7 — Add secrets on Streamlit Cloud (if not already done)
Go to your Streamlit app → **Manage app** (bottom right) → **Secrets** → paste:
```toml
ANTHROPIC_API_KEY = "your_anthropic_key_here"
```
Click **Save** — app restarts automatically.

---

## 🔐 How Login Works

1. **Register** — choose username + 4-digit PIN → creates a master blob on Walrus → stores blob ID locally in `registry.json`
2. **Login** — enter same username + PIN → fetches your master blob from Walrus → restores full state
3. **Auto-save** — every action (predict, resolve, hot take) saves a new blob and updates your registry entry
4. **Blob chain** — each blob stores the previous blob ID, creating a recoverable chain of your full history

> **Important**: `registry.json` maps your hashed credentials to your blob IDs. On Streamlit Cloud this persists within a session. For true cross-device persistence, note your latest Blob ID from the sidebar — you can always restore from it.

---

## 🌐 Switch to Mainnet

When ready to go live on Walrus mainnet:

**Option A — Streamlit Cloud secrets:**
```toml
ANTHROPIC_API_KEY = "your_key"
WALRUS_NETWORK = "mainnet"
```

**Option B — local .env:**
```
WALRUS_NETWORK=mainnet
```

The network badge in the sidebar shows `TESTNET` or `MAINNET` so you always know which network is active.

---

## 🏆 Leaderboard

The leaderboard is a single shared Walrus blob updated after every prediction resolution. Anyone can view it — no login needed for the leaderboard tab. The blob ID is shown publicly so anyone can verify the data on WalrusScan.

---

## 📁 Project Structure

```
walrus-grudge-analyst/
├── app.py                    # Main Streamlit app (v2)
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
├── .streamlit/
│   └── config.toml
├── utils/
│   ├── auth.py              # Username + PIN login, blob chain registry
│   ├── leaderboard.py       # Shared public leaderboard on Walrus
│   ├── walrus_memory.py     # Walrus store/retrieve + mainnet toggle
│   ├── roast_engine.py      # Claude AI roasts, praise, debate, grudges
│   ├── state_manager.py     # State management + blob chain support
│   └── wc2026_data.py       # WC2026 teams, fixtures, tournament data
└── README.md
```

---

## ⚡ Quick Local Run

```bash
pip install -r requirements.txt
cp .env.example .env   # add your ANTHROPIC_API_KEY
streamlit run app.py
```

---

## 🐳 Docker

```bash
docker build -t wc2026-grudge-agent .
docker run -p 8501:8501 \
  -e ANTHROPIC_API_KEY=your_key \
  -e WALRUS_NETWORK=testnet \
  wc2026-grudge-agent
```

---

## ❓ FAQ

**Q: What happens if I refresh the page?**  
A: Your session reloads but you just log back in — all your data is on Walrus and loads instantly.

**Q: What if Walrus testnet is down?**  
A: The app shows an error on save. Your in-session data stays intact. Try saving again when testnet recovers.

**Q: Is the free Anthropic API tier enough?**  
A: Yes. The app uses `claude-haiku-4-5` (cheapest model). Each roast costs fractions of a cent.

**Q: How do I move to mainnet?**  
A: Set `WALRUS_NETWORK=mainnet` in your environment or Streamlit secrets. That's it.

---

*Built for the Walrus Memory Agent challenge — Session 4. Powered by Walrus + Anthropic Claude.*
