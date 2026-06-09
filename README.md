# ⚽ WC2026 Grudge Agent

> A memory-powered FIFA World Cup 2026 prediction tracker that **roasts your bad calls**, **holds grudges forever**, and **debates your hot takes** — powered by Walrus testnet persistent memory + Claude AI.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red)
![Walrus](https://img.shields.io/badge/Walrus-Testnet-teal)
![Claude](https://img.shields.io/badge/Claude-Haiku-purple)

---

## 🎯 What It Does

| Feature | Description |
|---|---|
| 📝 **Prediction Tracker** | Log predictions for any WC2026 match or event |
| 🔥 **Roast Engine** | Claude roasts you when predictions are wrong — brutally |
| 😤 **Grudge System** | Every wrong call is stored; the agent references them forever |
| 💬 **Debate Partner** | Drop hot takes; the agent counters and calls out contradictions |
| 🧠 **Persistent Memory** | Full session memory stored as blobs on Walrus testnet |
| 🌊 **Blob ID Tracking** | Visible blob IDs link to WalrusScan for public proof |

---

## 🚀 Quick Start (Local)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/walrus-grudge-analyst.git
cd walrus-grudge-analyst
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment (optional)
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 4. Run the app
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🔑 API Keys

| Key | Where to Get | Required? |
|---|---|---|
| Anthropic API Key | [console.anthropic.com](https://console.anthropic.com) | Yes (free tier works!) |

> **Free tier note**: The app uses `claude-haiku-4-5` — the cheapest Claude model. Each roast costs ~0.001 credits. Free tier credits are more than enough for extensive testing.

---

## 🌊 Walrus Testnet Memory

This app stores all predictions, grudges, and hot takes as JSON blobs on **Walrus testnet**.

- **Publisher**: `https://publisher.walrus-testnet.walrus.space`
- **Aggregator**: `https://aggregator.walrus-testnet.walrus.space`
- **Explorer**: [walruscan.com/testnet](https://walruscan.com/testnet)

### How Memory Works
1. Make predictions & resolve them in the app
2. Click **💾 Save Memory to Walrus** — get a Blob ID
3. Copy your Blob ID somewhere safe
4. Next session: paste the Blob ID in the sidebar → **📥 Load Memory**
5. The agent remembers ALL past grudges and predictions 🧠

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo → set main file: `app.py`
4. Add secret in **Advanced settings**:
   ```
   ANTHROPIC_API_KEY = "your_key_here"
   ```
5. Click **Deploy** ✅

---

## 🐳 Deploy with Docker

```bash
# Build
docker build -t wc2026-grudge-agent .

# Run
docker run -p 8501:8501 -e ANTHROPIC_API_KEY=your_key wc2026-grudge-agent
```

---

## 📁 Project Structure

```
walrus-grudge-analyst/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker deployment
├── .env.example              # Environment template
├── .gitignore
├── .streamlit/
│   └── config.toml          # Streamlit theme config
├── utils/
│   ├── walrus_memory.py     # Walrus testnet store/retrieve
│   ├── roast_engine.py      # Claude roast/grudge/debate AI
│   ├── state_manager.py     # In-app state management
│   └── wc2026_data.py       # WC2026 fixtures & teams data
└── README.md
```

---

## 🔧 Environment Variables

| Variable | Description | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | (enter in UI) |
| `DEFAULT_USERNAME` | Pre-fill username | (empty) |

---

## 🏆 WC2026 Facts

- **Dates**: June 11 – July 19, 2026
- **Teams**: 48 (expanded format)
- **Matches**: 104
- **Hosts**: USA 🇺🇸 · Canada 🇨🇦 · Mexico 🇲🇽
- **Final**: MetLife Stadium, New York/New Jersey

---

## 🛠️ Troubleshooting

**Walrus save fails?**
- Walrus testnet can have intermittent downtime. Try again in a minute.
- Check [status.walrus.space](https://status.walrus.space) if available.

**Claude API errors?**
- Verify your API key at [console.anthropic.com](https://console.anthropic.com)
- Check you have credits (free tier is fine for this app)

**App won't start?**
```bash
pip install --upgrade -r requirements.txt
```

---

## 📄 License

MIT — build on it, fork it, deploy it. Just don't blame me when the agent roasts you for picking England to win it all. 🏴󠁧󠁢󠁥󠁮󠁧󠁿😤

---

*Built for Session 4 of the Walrus Memory Agent challenge. Powered by Walrus testnet + Anthropic Claude.*
