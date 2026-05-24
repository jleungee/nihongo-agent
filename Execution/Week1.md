# Week 1 — Foundation Setup (Zero-to-Hello-World)

**Before we start:** I'm skipping the "OpenClaw" install path and going directly to the underlying tools — Python, the OpenAI SDK pointed at Poe's OpenAI-compatible endpoint, and `python-telegram-bot`. Reason: for someone new to Linux, adding an extra framework on top of unfamiliar tooling triples the failure points, and most agent frameworks are thin wrappers around exactly these libraries anyway. By writing the gateway ourselves in ~80 lines of Python, you'll understand what's happening, and swapping in a heavier framework later (LangGraph, etc.) becomes trivial. **This is the data scientist's path: see the mechanics first.**

**A note on Poe:** Poe exposes an OpenAI-compatible REST API at `https://api.poe.com/v1`. That means we use the official `openai` Python SDK and just override the base URL. You get API access through a Poe subscription (required) — your subscription points are spent on each call. The benefit for you: one key gives you Claude Haiku/Sonnet/Opus, GPT-5, Gemini, and dozens of other bots. We'll start with `Claude-Haiku-4.5` because it's cheap and fast.

**Goal by Sunday night:** You send "hello" to your Telegram bot, Claude (via Poe) replies. The Python process keeps running. You can stop and start it cleanly.

That's it. No skills, no SQLite, no cron. Just plumbing.

---

## Day 1 (Mon) — Install WSL2 + Ubuntu 24.04

### What WSL2 actually is (intuitive)

WSL2 = "Windows Subsystem for Linux v2." Microsoft ships a tiny, fast Linux virtual machine that boots in ~1 second and shares your laptop's CPU, RAM, GPU, and disk with Windows. You access it through a terminal. Files inside it live in a hidden virtual disk; files in Windows are also reachable from inside it via `/mnt/c/...`.

**Why we use it:** every serious AI/agent tool is built for Linux first. Trying to do this on native Windows means fighting weird path bugs and missing libraries forever. WSL2 makes that pain go away.

### Step 1.1 — Open PowerShell as Administrator

1. Press the **Win** key.
2. Type `powershell`.
3. Right-click "Windows PowerShell" → **Run as administrator**.
4. Click **Yes** on the UAC prompt.

You should see a blue window with a prompt like `PS C:\WINDOWS\system32>`.

### Step 1.2 — Install WSL2 with Ubuntu 24.04

Paste this exact command and press Enter:

```powershell
wsl --install -d Ubuntu-24.04
```

**What happens:** Windows downloads the WSL2 kernel, enables the required virtualization features, and installs Ubuntu 24.04 LTS as the default distribution. This takes 3–10 minutes depending on internet speed.

You will likely be asked to reboot. **Reboot when asked.** After reboot, a black terminal window labeled "Ubuntu" should pop up automatically and continue installing for another minute or two.

### Step 1.3 — Create your Linux user

The Ubuntu window will eventually ask:

```
Enter new UNIX username:
```

Type a lowercase username with no spaces (e.g., `kenji`). Press Enter.

```
New password:
```

**Important:** Linux does NOT show any characters or asterisks while you type a password. The cursor doesn't move. **This is normal, not broken.** Type the password, press Enter, retype it when asked, press Enter again.

You'll land at a prompt that looks like:

```
kenji@DESKTOP-ABC123:~$
```

🎉 You are now inside Linux. That `~` means "your home folder," which is at `/home/kenji`.

### Step 1.4 — Confirm WSL2 (not WSL1) is being used

Open a new PowerShell window (doesn't need to be admin). Run:

```powershell
wsl -l -v
```

You should see:

```
  NAME            STATE           VERSION
* Ubuntu-24.04    Running         2
```

The `2` is what matters. If it says `1`, run:

```powershell
wsl --set-version Ubuntu-24.04 2
```

and wait for conversion (a few minutes).

### Pitfall corner — Day 1

- **"Virtualization not enabled" error:** Reboot into BIOS (usually F2 or Del at boot), find "Intel VT-x" or "Virtualization Technology," enable it, save & exit. On a 14900HX laptop this is almost always already on, but some OEMs ship it disabled.
- **Ubuntu window closed before user creation:** Open Start menu → type "Ubuntu" → click the Ubuntu app. It resumes setup.
- **Forgot Linux password:** From PowerShell run `wsl -u root passwd kenji` (replace `kenji` with your username). Sets a new one.
- **Ubuntu 24.04 not listed:** Make sure Windows is fully updated (`Settings → Windows Update`). WSL needs a recent Windows build to see the 24.04 image.

---

## Day 2 (Tue) — Linux Terminal Survival + Update System

You don't need to learn Linux deeply. You need to know ~10 commands to be productive.

### The 10 commands you'll use this week

| Command | What it does |
|---|---|
| `pwd` | print working directory (where am I?) |
| `ls` | list files in current folder |
| `ls -la` | list files including hidden (dotfiles) and details |
| `cd foldername` | change directory into `foldername` |
| `cd ..` | go up one folder |
| `cd ~` | go to your home folder |
| `mkdir name` | make new folder |
| `nano file.txt` | edit a text file in terminal (`Ctrl+O` save, `Ctrl+X` exit) |
| `cat file.txt` | print file contents to screen |
| `sudo <anything>` | run as administrator (will prompt your Linux password) |

That's enough. You'll pick up the rest by doing.

### Step 2.1 — Update Ubuntu

Open Ubuntu (Start menu → Ubuntu) and run:

```bash
sudo apt update && sudo apt upgrade -y
```

Type your Linux password when prompted. This downloads the latest package lists and upgrades everything. First run takes 5–15 minutes. Lots of green and white text will scroll by — totally fine.

**Intuitive picture:** `apt` is Ubuntu's app store, but command-line. `update` refreshes the catalog; `upgrade` actually installs new versions. The `-y` means "yes to all prompts."

### Step 2.2 — Install build essentials

```bash
sudo apt install -y build-essential curl wget git unzip ca-certificates
```

These are tools half of everything else depends on. Just install them and forget.

### Step 2.3 — Confirm git works

```bash
git --version
```

Should print something like `git version 2.43.x` (Ubuntu 24.04 ships a more recent git than 22.04). Configure your identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

These are just labels for any commits you make. They don't have to match GitHub yet.

---

## Day 3 (Wed) — Enable systemd + Install Node.js + Python 3.14

### Step 3.1 — Enable systemd

`systemd` is Linux's service manager. It's what lets you say "run my agent in the background and restart it if it crashes."

**Good news for Ubuntu 24.04:** unlike 22.04, Ubuntu 24.04 on WSL2 ships with `systemd` **enabled by default**. You can confirm with:

```bash
systemctl is-system-running
```

If output is `running` or `degraded`, you're done with this step. ✅

If it says `offline` (rare on 24.04), do the manual fix:

```bash
sudo nano /etc/wsl.conf
```

Type these exact lines:

```ini
[boot]
systemd=true
```

Save (`Ctrl+O`, `Enter`), exit (`Ctrl+X`). Then in **PowerShell**:

```powershell
wsl --shutdown
```

Wait 10 seconds, reopen Ubuntu, and re-run `systemctl is-system-running`.

### Step 3.2 — Install Node.js 22 via nvm

We use `nvm` (Node Version Manager) instead of `apt install nodejs` because Ubuntu's apt version is older. `nvm` lets you switch Node versions per project later.

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```

This pipes a shell script directly into bash. (In production you'd inspect it first; for `nvm` specifically it's been the standard install method for ~10 years.)

Now reload your shell so the `nvm` command becomes available:

```bash
source ~/.bashrc
```

Install Node 22:

```bash
nvm install 22
nvm use 22
node --version
```

Should print `v22.x.x`.

### Step 3.3 — Install Python 3.14 + venv

Ubuntu 24.04 ships Python 3.12 as the system Python. We want **3.14** for the latest features (the `t` free-threaded variant, faster startup, sub-interpreter support, better error messages). We get it from the well-maintained `deadsnakes` PPA.

```bash
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.14 python3.14-venv python3.14-dev
```

Verify:

```bash
python3.14 --version
```

Should print `Python 3.14.x`.

> **Heads-up about 3.14:** It's still early in its life cycle as of May 2026 — most popular libraries (`openai`, `python-telegram-bot`, `python-dotenv`) ship pure-Python wheels and work fine, but if later in your project you hit a library that doesn't yet have a 3.14 wheel (rare, but happens with native-compiled packages like `numpy`, `cryptography`, etc.), you have two options: (a) wait a few weeks for upstream wheels, or (b) drop the project venv to 3.13 — which is a one-line change. We'll cross that bridge if we hit it. For Week 1, you're 100% safe on 3.14.

**About venv (intuitive):** A venv is a private Python install for one project. Each project's libraries are isolated from each other and from the system Python. This is non-negotiable best practice — every Python project gets its own venv.

---

## Day 4 (Thu) — VS Code + Project Structure

### Step 4.1 — Install VS Code on Windows (if you don't have it)

Download from [https://code.visualstudio.com/](https://code.visualstudio.com/) and install normally **on Windows**. Don't install it inside Ubuntu — VS Code lives on Windows but reaches into Ubuntu via an extension.

### Step 4.2 — Install the WSL extension

1. Open VS Code on Windows.
2. Click the Extensions icon on the left sidebar (four squares).
3. Search **"WSL"** — install the official Microsoft one.
4. Search **"Python"** — install the official Microsoft one.
5. Restart VS Code.

### Step 4.3 — Open Ubuntu folder in VS Code

In Ubuntu terminal:

```bash
cd ~
mkdir nihongo-agent
cd nihongo-agent
code .
```

The `code .` command tells WSL to launch VS Code on Windows, attached to the current Linux folder. The first time it runs it auto-installs a small "VS Code server" inside Ubuntu. This takes ~30 seconds.

VS Code opens. The bottom-left corner should say **"WSL: Ubuntu-24.04"** in a colored badge. That's your confirmation that VS Code is editing files inside Linux, not Windows.

### Step 4.4 — Create the project skeleton

Inside VS Code, open the integrated terminal (`` Ctrl+` `` — the backtick key, top-left of keyboard). It opens a Linux shell already `cd`'d into `nihongo-agent`.

Run:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
```

You'll notice your prompt changes to start with `(.venv)`. That means you're now inside the project's venv. Any `pip install` from here only affects this project.

Install the libraries:

```bash
pip install --upgrade pip
pip install python-telegram-bot openai python-dotenv
```

Why `openai` and not `anthropic`: Poe's API is OpenAI-compatible. We use the OpenAI SDK and just point it at `https://api.poe.com/v1`. Same code shape, different base URL.

Create the project layout:

```bash
mkdir -p skills logs data
touch agent.py .env .gitignore
```

In the file tree on the left of VS Code you should now see:

```
nihongo-agent/
├── .venv/        (auto-created, ignore)
├── data/
├── logs/
├── skills/
├── .env
├── .gitignore
└── agent.py
```

Open `.gitignore` and paste:

```gitignore
.venv/
.env
__pycache__/
*.pyc
logs/
data/*.db
```

This prevents you from ever committing your API keys or your venv to git.

---

## Day 5 (Fri) — Get Your Two API Keys

### Step 5.1 — Telegram bot token

1. On your phone or desktop, open Telegram.
2. Search for **@BotFather** (verified blue check).
3. Start a chat with it, send `/newbot`.
4. It asks for a display name → type something like `Nihongo Sensei`.
5. It asks for a username → must end in `bot`, e.g., `kenji_nihongo_bot`.
6. It replies with a token like `7891234567:AAH-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`.

Copy that token. **Anyone with it can control your bot, so treat it like a password.**

7. Search for **@userinfobot** in Telegram, start chat, send any message. It replies with your user ID (a number like `123456789`). Save this — we'll use it to make sure the bot only talks to you.

### Step 5.2 — Poe API key

The Poe API requires an active **Poe subscription** (any tier — even the cheapest gives enough monthly points for personal agent use).

1. Go to [https://poe.com/](https://poe.com/) and sign in (or sign up).
2. If you don't already have a subscription, go to **Settings → Subscription** and pick a tier. The cheapest monthly plan is plenty for Week 1–8.
3. Once subscribed, go to [https://poe.com/api_key](https://poe.com/api_key).
4. Click **"Create new key"** (or copy the existing one). It's a long string — treat it like a password.

> **A note on cost model:** Unlike Anthropic where you pay per token, Poe deducts **points** from your subscription's monthly allowance. Each model has a different points cost per message (Haiku ~30 points/msg, Sonnet ~200, Opus ~3000+). For Week 1's hello-world test, you'll spend a trivial amount. The dashboard at `poe.com/settings` shows live point usage.

### Step 5.3 — Save keys in `.env`

In VS Code, open `.env` and paste (with your actual values):

```bash
TELEGRAM_BOT_TOKEN=7891234567:AAH-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TELEGRAM_OWNER_ID=123456789
POE_API_KEY=your-poe-api-key-here
POE_MODEL=Claude-Haiku-4.5
```

Save (`Ctrl+S`). Because `.env` is in `.gitignore`, this file never leaves your laptop.

> **About `POE_MODEL`:** On Poe, model names are bot names. `Claude-Haiku-4.5` is the cheap fast one we'll use as default. Later you can switch to `Claude-Sonnet-4.5` for harder reasoning, `Claude-Opus-4.1` for the heaviest stuff, or `GPT-5` / `Gemini-2.5-Pro` to compare. Just edit this one line — no code changes needed.

---

## Day 6 (Sat) — Write the Minimal Agent

Open `agent.py` in VS Code and paste this **complete** file:

```python
"""
Nihongo Agent - Week 1 minimal version.
Listens to Telegram, forwards to Claude (via Poe), replies.
This is the gateway. In Week 2 we route to skills instead of always calling the LLM.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# --- Setup ---
load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OWNER_ID = int(os.environ["TELEGRAM_OWNER_ID"])
POE_API_KEY = os.environ["POE_API_KEY"]
POE_MODEL = os.environ.get("POE_MODEL", "Claude-Haiku-4.5")

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_DIR / "agent.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("nihongo")

# Poe is OpenAI-compatible: same SDK, different base URL.
client = OpenAI(
    api_key=POE_API_KEY,
    base_url="https://api.poe.com/v1",
)

SYSTEM_PROMPT = (
    "You are Nihongo Sensei, a kind and patient Japanese tutor. "
    "When the user writes in Japanese, reply in Japanese first, then add a brief "
    "English gloss in parentheses. When the user writes in English, answer in "
    "English but include relevant Japanese examples. Keep replies short (≤4 sentences) "
    "unless explicitly asked for more depth."
)

# --- Handlers ---
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        log.warning("Rejected /start from %s", update.effective_user.id)
        return
    await update.message.reply_text(
        "こんにちは！I'm your Nihongo Sensei. Send me anything in Japanese "
        "or English and let's start learning."
    )

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        log.warning("Rejected message from %s", update.effective_user.id)
        return

    user_text = update.message.text
    log.info("USER: %s", user_text)

    try:
        response = client.chat.completions.create(
            model=POE_MODEL,
            max_tokens=512,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
        )
        reply = response.choices[0].message.content
    except Exception as e:
        log.exception("Poe call failed")
        reply = f"⚠️ Error talking to Poe: {e}"

    log.info("BOT: %s", reply)
    await update.message.reply_text(reply)

# --- Main ---
def main():
    log.info("Starting agent... (model=%s)", POE_MODEL)
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    log.info("Polling Telegram. Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
```

Save the file.

**What changed from the Anthropic version:**
- Imported `OpenAI` from `openai` instead of `Anthropic` from `anthropic`.
- Constructed the client with `base_url="https://api.poe.com/v1"`.
- Used `client.chat.completions.create(...)` (OpenAI shape) instead of `client.messages.create(...)` (Anthropic shape).
- The `system` prompt becomes the first message with `role="system"` instead of a top-level kwarg.
- Read the assistant text from `response.choices[0].message.content`.

Everything else is identical.

### Step 6.1 — Run it

In the VS Code terminal (make sure you see `(.venv)` in the prompt; if not, run `source .venv/bin/activate`):

```bash
python agent.py
```

You should see:

```
2026-05-23 14:00:00 [INFO] Starting agent... (model=Claude-Haiku-4.5)
2026-05-23 14:00:01 [INFO] Polling Telegram. Press Ctrl+C to stop.
```

The process is now alive and listening.

### Step 6.2 — Talk to it

On your phone, open Telegram, find your bot (search the username you gave BotFather, e.g., `@kenji_nihongo_bot`), and send `/start`.

You should get the welcome message back.

Send: `Hello, can you teach me how to say good morning in Japanese?`

The bot will show "typing..." for 1–3 seconds, then reply with something like:

> おはようございます (ohayou gozaimasu) — "good morning."

🎉 **Your agent is alive.**

In the VS Code terminal you'll see your messages and the model's replies logged.

To stop the agent, click the terminal and press `Ctrl+C`.

---

## Day 7 (Sun) — Make It Auto-Start

Right now the agent only runs while VS Code's terminal is open. We want it to start with WSL and stay running. This is where systemd earns its keep.

### Step 7.1 — Find your project's absolute path

In the terminal:

```bash
pwd
```

Should print something like `/home/kenji/nihongo-agent`. Copy this exact path.

Also find your venv's Python:

```bash
which python
```

Should print `/home/kenji/nihongo-agent/.venv/bin/python`. Copy this too.

### Step 7.2 — Create the systemd service file

```bash
sudo nano /etc/systemd/system/nihongo-agent.service
```

Paste (replace `kenji` with your Linux username and the paths if yours differ):

```ini
[Unit]
Description=Nihongo Agent (Telegram + Poe)
After=network.target

[Service]
Type=simple
User=kenji
WorkingDirectory=/home/kenji/nihongo-agent
ExecStart=/home/kenji/nihongo-agent/.venv/bin/python /home/kenji/nihongo-agent/agent.py
Restart=on-failure
RestartSec=5
StandardOutput=append:/home/kenji/nihongo-agent/logs/systemd.log
StandardError=append:/home/kenji/nihongo-agent/logs/systemd.log

[Install]
WantedBy=multi-user.target
```

Save (`Ctrl+O`, `Enter`) and exit (`Ctrl+X`).

### Step 7.3 — Enable and start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable nihongo-agent
sudo systemctl start nihongo-agent
```

Check status:

```bash
sudo systemctl status nihongo-agent
```

You should see green **"active (running)"**. Press `q` to exit the status view.

### Step 7.4 — Test the auto-restart

Send a message to your bot from Telegram — it should still reply, even though you closed the manual `python agent.py`.

To see live logs:

```bash
tail -f logs/systemd.log
```

(Press `Ctrl+C` to stop tailing.)

To stop the service (e.g., to debug):

```bash
sudo systemctl stop nihongo-agent
```

To restart after editing code:

```bash
sudo systemctl restart nihongo-agent
```

### Step 7.5 — Make WSL auto-start with Windows

By default, WSL only runs when you open it. We want it always-on so the agent works even if you haven't opened a terminal.

Open a Windows PowerShell (admin), run:

```powershell
wsl --set-default Ubuntu-24.04
```

Then create a Windows scheduled task to start WSL on login. The simplest way: press `Win+R`, type `shell:startup`, press Enter. A Windows folder opens. Right-click → **New → Shortcut**. Target:

```
C:\Windows\System32\wsl.exe -d Ubuntu-24.04 --exec dbus-launch true
```

Name it `Start Nihongo Agent`. Done. Now every time you log into Windows, WSL boots and your agent starts.

---

## End-of-Week Checklist

By Sunday night you should be able to honestly tick all of these:

- [ ] You can open Ubuntu from the Start menu and see a `$` prompt.
- [ ] You know what `cd`, `ls`, `nano`, `sudo` do.
- [ ] `node --version` shows v22, `python3.14 --version` shows 3.14.
- [ ] VS Code opens your project with "WSL: Ubuntu-24.04" in the corner.
- [ ] `.env` exists with four keys (Telegram token + owner ID + Poe key + Poe model), and `.gitignore` excludes it.
- [ ] You sent a message to your Telegram bot and got a Claude-via-Poe reply.
- [ ] `sudo systemctl status nihongo-agent` shows "active (running)".
- [ ] You can reboot your laptop, and the bot still replies without you doing anything.

If all 8 boxes are ticked: **foundation done.** Week 2 we add SQLite, the first card pool, and the daily quiz cron.

---

## Common Week-1 Pitfalls (read this before getting stuck)

**"`code .` doesn't open VS Code"** — VS Code wasn't installed on Windows yet, or the WSL extension isn't installed. Install both, restart VS Code, try again.

**"`pip install` fails with permission errors"** — You forgot to activate the venv. Look at your prompt: if it doesn't start with `(.venv)`, run `source .venv/bin/activate` and retry.

**"`pip install openai` fails with a build/wheel error on Python 3.14"** — Rare, but if it happens with a transitive dependency, the cleanest fix is to recreate the venv on 3.13: `deactivate && rm -rf .venv && python3.13 -m venv .venv && source .venv/bin/activate && pip install python-telegram-bot openai python-dotenv`. (You'll need `sudo apt install python3.13 python3.13-venv` first.)

**"Bot replies once then stops responding"** — Probably hit a Poe API error (bad key, no active subscription, ran out of points). Check `logs/agent.log`. Look for the error line.

**"systemctl says 'System has not been booted with systemd'"** — Surprising on 24.04, but if it happens: re-check `/etc/wsl.conf` has `[boot]\nsystemd=true`, then fully shut WSL down with `wsl --shutdown` from PowerShell (not just close the terminal), then reopen Ubuntu.

**"Telegram bot ignores my messages"** — `TELEGRAM_OWNER_ID` doesn't match your real user ID. Send a message to `@userinfobot` again, copy the ID exactly, edit `.env`, restart the service.

**"Poe returns 401 unauthorized"** — Either the key is wrong, or your subscription lapsed. Check `poe.com/settings` and regenerate the key if needed.

**"Poe returns 429 / 'insufficient points'"** — You burned through your monthly point allotment. Either upgrade tier, switch `POE_MODEL` to a cheaper bot (e.g., `Claude-Haiku-4.5` is much cheaper than `Claude-Opus-4.1`), or wait for the monthly reset.

**"Poe returns 'model not found'"** — Bot names on Poe are case-sensitive and use hyphens. Double-check the spelling in `.env` (e.g., `Claude-Haiku-4.5`, not `claude-haiku-4.5` or `claude-haiku-4-5`). When in doubt, browse to `poe.com` and check the exact bot name in the URL or header.

**"It's slow (5+ seconds per reply)"** — First call is always slower (cold connection). Sustained replies should be 1–2 seconds with Haiku. If consistently slow, your Wi-Fi is the bottleneck, not the agent.

---

## What you've actually built

Even though this is "just a chatbot," you now have:

- A **Linux dev environment** on Ubuntu 24.04 LTS (supported until 2029) that survives reboots.
- A **Python 3.14 project** with proper venv hygiene.
- A **secrets file** that's git-ignored.
- A **service** that auto-restarts on crash.
- A **gateway pattern** — `on_message` is the single entry point that, in Week 2, will route to skills instead of going straight to the LLM.
- **Model-agnostic plumbing** — because Poe is OpenAI-compatible and we read the model name from `.env`, you can swap from `Claude-Haiku-4.5` to `Claude-Opus-4.1` to `GPT-5` by editing one line.
- **Logs in two places** (Python's own + systemd's capture) for when things go wrong.

That `on_message` function is exactly where the "router" we discussed earlier will live. Next week we'll change it from "always send to the LLM" to "ask Haiku which skill should handle this, then dispatch to that skill's tools." The architecture grows; this foundation doesn't change.

When you're done, ping me with which checklist boxes are ticked and I'll write **Week 2** (SQLite + first 50 cards + the FSRS scheduler + the daily 08:00 quiz cron).