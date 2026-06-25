# 🪟 Windows Setup Guide — Lahore PM2.5 Live Dashboard

Complete step-by-step guide to get the Streamlit dashboard running on your Windows PC, updating automatically every day.

**Time required:** ~30 minutes first time

---

## Step 1 — Install Python

1. Go to https://www.python.org/downloads/
2. Download **Python 3.11** (recommended)
3. Run the installer
4. ✅ **Critical:** Check **"Add Python to PATH"** before clicking Install
5. Verify in Command Prompt:
   ```
   python --version
   ```
   Should print: `Python 3.11.x`

---

## Step 2 — Download the Project

**Option A — Git (recommended):**
```cmd
git clone https://github.com/your-username/lahore-pm25.git
cd lahore-pm25
```

**Option B — Manual:**
1. Download the project ZIP
2. Extract to a folder e.g. `C:\Users\YourName\lahore-pm25`
3. Open Command Prompt and navigate there:
   ```cmd
   cd C:\Users\YourName\lahore-pm25
   ```

---

## Step 3 — Run the Setup Script

Double-click `setup.bat` — or run it from Command Prompt:

```cmd
setup.bat
```

This will:
- ✅ Check Python is installed
- ✅ Create a virtual environment (`venv\`)
- ✅ Install all Python packages from `requirements.txt`
- ✅ Create all required folders (`data\`, `models\`, `logs\`)
- ✅ Create a `.env` template for your API keys
- ✅ Run a demo pipeline to verify everything works

**Expected output (last few lines):**
```
Demo pipeline succeeded!
Setup complete!
```

If you see errors, check that Python is installed and `requirements.txt` is present.

---

## Step 4 — Add Your API Keys

Open `.env` in Notepad and fill in your keys:

```env
NASA_FIRMS_KEY=your_firms_key_here
IQAIR_API_KEY=your_iqair_key_here
OPENAQ_KEY=optional
```

See `API_KEYS_SETUP.md` for instructions on getting each key (all free).

> **Don't have keys yet?** No problem — the tool works with demo data until you add them. Come back to this step later.

---

## Step 5 — Launch the Dashboard

```cmd
streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`

You'll see:
- Live AQI and pollutant readings
- Source apportionment breakdown (Vehicle, Crop Burning, Industry...)
- 7-day forecast chart
- Historical trends

**To stop the dashboard:** Press `Ctrl+C` in the terminal

---

## Step 6 — Schedule Daily Automation

This makes the pipeline run every morning automatically — even if you don't open it.

### 6a. Open Task Scheduler

1. Press `Win + R`
2. Type `taskschd.msc` → Enter
3. In the right panel click **"Create Basic Task..."**

### 6b. Configure the task

| Setting | Value |
|---------|-------|
| Name | `Lahore PM2.5 Daily` |
| Description | `Fetches live air quality data and runs source apportionment` |
| Trigger | Daily |
| Start time | `07:00 AM` |
| Action | Start a program |
| Program | Browse to `C:\Users\YourName\lahore-pm25\run_pipeline.bat` |
| Start in | `C:\Users\YourName\lahore-pm25` |

### 6c. Verify it works

Right-click the task → **"Run"** → check `logs\` folder for a new log file.

---

## Step 7 — Keep the Dashboard Always Open

### Option A — Pin to taskbar (simple)
1. Run `streamlit run app.py` once
2. In Chrome, go to ⋮ menu → **"Save and share"** → **"Create shortcut"**
3. Check "Open as window" → Add to taskbar

### Option B — Auto-start with Windows (advanced)

Create a shortcut to this batch file and place it in your Windows Startup folder:

**start_dashboard.bat** (create this file):
```bat
@echo off
cd /d C:\Users\YourName\lahore-pm25
call venv\Scripts\activate
start streamlit run app.py
timeout /t 4
start chrome http://localhost:8501
```

**Add to Windows startup:**
1. Press `Win + R`
2. Type `shell:startup` → Enter
3. Copy your `start_dashboard.bat` shortcut into this folder

Now the dashboard opens automatically every time you start Windows.

---

## Step 8 — (Optional) Set Up Telegram Alerts

Get a message on your phone when PM2.5 is dangerously high.

### 8a. Create a Telegram bot
1. Open Telegram → search **@BotFather**
2. Send `/newbot` → follow instructions
3. Copy the bot token
4. Message your bot once (to activate the chat)
5. Get your chat ID by visiting:
   `https://api.telegram.org/bot<TOKEN>/getUpdates`

### 8b. Add to .env
```env
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
PM25_ALERT_THRESHOLD=35
```

### 8c. Add to run_pipeline.bat

Add this line at the end of `run_pipeline.bat`:
```bat
python scripts\08_alerts.py
```

*(Script 08 is the alert sender — see scripts folder)*

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python not found` | Reinstall Python, check "Add to PATH" |
| `streamlit not found` | Run `pip install streamlit` in the venv |
| Dashboard shows demo data | Run `run_pipeline.bat` first, then refresh |
| Task Scheduler not running | Right-click task → Properties → set "Run whether user is logged on or not" |
| Port 8501 in use | Run `streamlit run app.py --server.port 8502` |
| Chrome doesn't open | Navigate manually to `http://localhost:8501` |

---

## Folder Structure After Setup

```
lahore-pm25\
├── app.py                  ← Streamlit dashboard (run this)
├── setup.bat               ← One-time setup
├── run_pipeline.bat        ← Daily data update
├── requirements.txt
├── .env                    ← Your API keys (keep private)
├── data\
│   ├── live\               ← Today's readings (updated daily)
│   ├── forecast\           ← 7-day forecast
│   └── processed\          ← Historical data
├── models\                 ← Trained ML model
├── logs\                   ← Daily run logs
└── scripts\
    ├── 07_iqair_live.py    ← Live data fetcher
    ├── 06_forecast.py      ← Forecast generator
    └── ...
```

---

## Daily Workflow (after setup)

Once everything is set up, your daily experience is:

1. **7:00 AM** — Task Scheduler runs `run_pipeline.bat` automatically
2. **Open browser** → `http://localhost:8501`
3. See today's PM2.5 with source breakdown, already updated
4. Dashboard auto-refreshes every 5 minutes throughout the day

That's it. The pipeline handles everything else.
