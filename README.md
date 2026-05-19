# 🔊 Discord TTS Bot — Railway Deployment

A Discord bot that speaks text aloud in voice channels using Google TTS (gTTS).
Fully configured for **one-click Railway deployment**.

---

## 🚀 Deploy to Railway

### Option A — Deploy via GitHub (Recommended)

1. Push this folder to a **GitHub repository**
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Select your repository
4. Go to your service → **Variables** tab → add:
   ```
   DISCORD_TOKEN = your_bot_token_here
   PREFIX        = !
   ```
5. Railway will auto-detect `nixpacks.toml` and install **ffmpeg + Python + dependencies**
6. Your bot goes live in ~2 minutes ✅

### Option B — Deploy via Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Inside the project folder
railway init
railway up

# Set env vars
railway variables set DISCORD_TOKEN=your_token_here
railway variables set PREFIX=!
```

---

## 🤖 Create a Discord Bot

1. Go to https://discord.com/developers/applications → **New Application**
2. **Bot** tab → **Reset Token** → copy token
3. Enable **Message Content Intent** under Privileged Gateway Intents
4. **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Send Messages`, `Connect`, `Speak`, `Use Voice Activity`, `Add Reactions`
5. Open the generated URL to invite the bot to your server

---

## 💬 Commands

### Prefix Commands (default: `!`)

| Command | Description | Example |
|---------|-------------|---------|
| `!tts <text>` | Speak text (English) | `!tts Hello world` |
| `!tts <lang> <text>` | Speak in a language | `!tts hindi नमस्ते` |
| `!join` | Join your voice channel | `!join` |
| `!leave` | Leave voice channel | `!leave` |
| `!stop` | Stop playback | `!stop` |
| `!langs` | List supported languages | `!langs` |
| `!ping` | Check bot latency | `!ping` |

### Slash Commands

| Command | Description |
|---------|-------------|
| `/tts text: ... language: ...` | Speak text in voice channel |
| `/join` | Join voice channel |
| `/leave` | Disconnect from voice |
| `/stop` | Stop playback |

---

## 🌐 Supported Languages

| Name | Code |
|------|------|
| english | en |
| hindi | hi |
| french | fr |
| spanish | es |
| german | de |
| japanese | ja |
| korean | ko |
| arabic | ar |
| russian | ru |
| italian | it |
| portuguese | pt |
| chinese | zh |

---

## 📁 File Structure

```
discord_tts_railway/
├── bot.py            # Main bot code
├── requirements.txt  # Python dependencies
├── Procfile          # Process definition
├── nixpacks.toml     # Railway build config (installs ffmpeg)
├── railway.json      # Railway deploy config
└── README.md         # This file
```

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_TOKEN` | ✅ Yes | — | Your Discord bot token |
| `PREFIX` | No | `!` | Command prefix |

---

## 🛠️ Local Development

```bash
pip install -r requirements.txt

# Install ffmpeg
# macOS:   brew install ffmpeg
# Ubuntu:  sudo apt install ffmpeg
# Windows: https://ffmpeg.org/download.html

export DISCORD_TOKEN="your_token_here"
python bot.py
```
