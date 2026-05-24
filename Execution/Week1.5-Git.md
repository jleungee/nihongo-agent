Yes — strongly recommended, before you write another line of Week 2 code.

A few reasons specific to where you are:

**You're about to make architectural changes.** Week 2 refactors `agent.py` into a router and introduces `skills/`. If you break something subtly mid-week, you'll want to `git diff` against "Week 1 known-good" to find what changed. Without a baseline commit, you have nothing to diff against.

**You'll start storing real personal data.** `data/nihongo.db` will contain your review history. That's data you don't want to lose to an `rm -rf` typo or a WSL filesystem hiccup. GitHub becomes your offsite backup almost for free (for the *code*, not the DB — see below).

**Secrets hygiene gets harder later.** Right now you have one `.env` with two tokens. Easy to gitignore. By Week 4 you might have API keys for JMdict, OpenAI, etc. Establishing the `.gitignore` discipline now means you never commit a secret.

---

## Before you `git push`, run this checklist

### 1. Verify your `.gitignore` is doing its job

Create or update `.gitignore` in the project root:

```
# Secrets
.env
.env.*
!.env.example

# Python
__pycache__/
*.pyc
.venv/
venv/
*.egg-info/

# Data — never commit your personal study DB
data/*.db
data/*.db-wal
data/*.db-shm
data/backups/

# Logs
logs/
*.log

# Editor
.vscode/
.idea/
*.swp
.DS_Store
```

Then sanity check:

```bash
git status
```

You should **not** see `.env`, `data/nihongo.db`, or `logs/` in the output. If you do, the gitignore isn't matching — fix it before committing.

### 2. Commit a `.env.example` instead

So future-you (or anyone reading the repo) knows what env vars are needed:

```bash
cat > .env.example <<'EOF'
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
TELEGRAM_OWNER_ID=your-numeric-telegram-user-id
POE_API_KEY=your-poe-api-key
POE_MODEL=Claude-Haiku-4.5
EOF
```

### 3. Double-check no secret has ever been added

```bash
git log --all --full-history -- .env 2>/dev/null
grep -rn "TELEGRAM_BOT_TOKEN=" . --exclude-dir=.git --exclude=.env --exclude=.env.example
```

The first should print nothing. The second should only show matches in code that *reads* the env var (e.g., `os.environ["TELEGRAM_BOT_TOKEN"]`), never the actual token value.

### 4. Add a minimal `README.md`

Future-you in three months will thank present-you:

```markdown
# Nihongo Agent

Personal Japanese tutor + spaced-repetition bot running on WSL2, accessed via Telegram.

## Stack
- Python 3.x, python-telegram-bot, OpenAI SDK pointed at Poe
- SQLite for cards/reviews
- systemd (user) for service management
- Claude Haiku 4.5 via Poe API

## Setup
1. `cp .env.example .env` and fill in tokens
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `sqlite3 data/nihongo.db < data/schema.sql`
5. `python seed_cards.py`
6. `python agent.py` (or install the systemd unit)

## Status
- [x] Week 1: Telegram ↔ Poe chat, systemd service
- [ ] Week 2: SQLite + spaced repetition + daily quiz
```

### 5. Pin your dependencies

```bash
pip freeze > requirements.txt
```

### 6. Make the repo **private**

When you create it on GitHub, choose **Private**. Even with secrets gitignored, your card content is personal, and a private repo has zero downside for a solo project. You can flip it public later if you ever want to.

---

## The actual commands

```bash
cd ~/nihongo-agent
git init
git branch -M main
git add .
git status   # eyeball this carefully — confirm no .env, no .db
git commit -m "Week 1 complete: Telegram bot with Poe chat, systemd service"
```

Then on GitHub: create empty private repo `nihongo-agent` (no README, no gitignore — you already have them). Then:

```bash
git remote add origin git@github.com:<your-username>/nihongo-agent.git
git push -u origin main
```

If you haven't set up SSH keys for GitHub on WSL yet, use HTTPS + a personal access token, or do the SSH key setup now (10 minutes, worth it).

---

## One more thing — branch per week (optional but nice)

Since you're working through a structured plan, consider branching per week:

```bash
git checkout -b week2
# ... work all week ...
git push -u origin week2
# When week 2 passes the checklist:
git checkout main
git merge week2
git push
```

This way `main` always represents "last known fully working state" and you can experiment freely on week branches. If Week 2 goes sideways on Wednesday, `git checkout main` gets you back to working Week 1 instantly.

If that feels like ceremony for a solo project — it kind of is — just commit on `main` after each day's checklist passes. Either is fine; the important thing is regular commits, not the branching strategy.

---

**Bottom line:** spend 15 minutes pushing now. You'll never regret having Week 1 archived as a clean git tag, and you'll absolutely regret it if you don't and need to roll back from a Wednesday-night refactor gone wrong.