# Attendance Check

Get a phone notification when a PollEv poll unlocks during class.

## How it works

A Playwright browser on a VPS loads the professor's PollEv participant page every 10 seconds. When the poll transitions from locked to unlocked, it sends a push notification via [ntfy.sh](https://ntfy.sh).

```
VPS (cron, MW 2:25pm)
  └── main.py
        ├── Playwright loads PollEv page
        ├── Reads page text to detect state (no_poll / locked / unlocked)
        ├── Detects locked → unlocked transition
        └── Sends push notification via ntfy.sh
```

## Setup

### Requirements

- Python 3.11+
- A VPS or server (runs headless Chromium via Playwright)
- [ntfy.sh](https://ntfy.sh) app on your phone

### Install

```bash
git clone https://github.com/patrick0f/attendance-check.git
cd attendance-check
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
playwright install-deps chromium
```

### Configure

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```
NTFY_TOPIC=your-ntfy-topic
POLLEV_URL=https://pollev.com/your-presenter-slug
```

### Run

```bash
python3 -m src.main
```

### Test

```bash
make test
```

### Cron (auto-run MW 2:25pm)

```bash
make install-cron
```

## Project structure

```
src/
  checker.py   # Playwright PollEv page reader + state parser
  detect.py    # Locked → unlocked transition detection + cooldown
  notify.py    # ntfy.sh push notifications
  main.py      # Entry point + poll loop
  config.py    # Settings from .env
tests/
  test_checker.py
  test_detect.py
  test_notify.py
```
