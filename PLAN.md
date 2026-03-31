# Attendance Check Detector — Plan

## Context

The course uses PollEv for attendance. The professor has a standing PollEv question that stays locked, then unlocks it at an unpredictable time during lecture for students to respond. Goal: detect when the poll unlocks and send a phone notification.

**Schedule:** Monday/Wednesday 2:30pm–3:45pm
**PollEv URL:** https://pollev.com/<PRESENTER_SLUG>

## Approach: Poll PollEv Directly
**HTTP poll the PollEv participant page every 10 seconds.** When the professor unlocks responses, the page state changes. We detect that transition and send a push notification. No video, no OCR, no Panopto auth needed.

### Architecture

```
VPS (Ubuntu) — already set up at <VPS_IP>
├── cron (starts at 2:25pm MW)
│   └── main.py
│       ├── HTTP GET pollev.com/<PRESENTER_SLUG> every 10s
│       ├── Detect: poll locked → unlocked transition
│       └── ntfy.sh → phone push notification
```

### How PollEv Works

- Professor's page: `pollev.com/<PRESENTER_SLUG>`
- When locked: question is visible but response form is disabled/hidden
- When unlocked: response form becomes active
- We need to detect the locked→unlocked transition

### Detection Strategy

Two possible approaches (need to test which works):

1. **Scrape the participant page** — fetch the HTML, check if the response form is active vs locked
2. **Use PollEv's API** — PollEv's frontend likely calls an API to check poll status. Intercept and use those endpoints directly (more reliable, less likely to break)

We'll start by inspecting what the page looks like in both states to determine the right selectors/API calls.

### Components

#### 1. Poll Checker (`src/checker.py`)
- HTTP request to PollEv every 10 seconds
- Parse response to determine: locked, unlocked, or no active poll
- No browser needed — just `requests` or lightweight fetch

#### 2. Detection (`src/detect.py`)
- Track state transitions: locked → unlocked = alert
- Cooldown to avoid repeat notifications
- Already built and tested (18 tests passing) — adapt from OCR-based to state-based

#### 3. Notification (`src/notify.py`)
- Already built and tested (4 tests passing)
- ntfy.sh push to phone
- Heartbeat at startup, alert on unlock

#### 4. Main Loop (`src/main.py`)
```
1. Send heartbeat notification
2. Every 10 seconds:
   a. Check PollEv page/API status
   b. If unlocked + cooldown expired → send alert
   c. Log result
3. Exit after 3:45pm
```

#### 5. Scheduling
- **cron**: `25 14 * * 1,3` — same as before
- VPS already running at <VPS_IP>

### Config (`src/config.py`)
```python
CONFIG = {
    "poll_interval_seconds": 10,
    "alert_cooldown_seconds": 180,
    "ntfy_topic": "<NTFY_TOPIC>",
    "pollev_url": "https://pollev.com/<PRESENTER_SLUG>",
    "class_end_time": "15:45",
    "timezone": "America/New_York",
}
```

## What We Keep

- `src/detect.py` + tests — adapt detection logic
- `src/notify.py` + tests — unchanged
- `src/config.py` — update keys
- `Makefile` — unchanged
- VPS at <VPS_IP> — already provisioned

## File Structure

```
attendance-check/
├── src/
│   ├── main.py            # entry point + main loop
│   ├── config.py          # settings
│   ├── checker.py         # PollEv status checker (NEW)
│   ├── detect.py          # state transition detection (adapt)
│   └── notify.py          # ntfy.sh integration (keep)
├── tests/
│   ├── test_checker.py    # PollEv checker tests (NEW)
│   ├── test_detect.py     # detection tests (adapt)
│   └── test_notify.py     # notification tests (keep)
├── Makefile
├── requirements.txt       # just: requests, python-dotenv, pytest
└── .env                   # secrets (gitignored)
```

## Implementation Order

1. **Inspect PollEv page** — fetch the page in both locked/unlocked states, find the right signal
2. `src/checker.py` + `tests/test_checker.py` — TDD the PollEv status checker
3. Adapt `src/detect.py` — change from OCR text matching to state transition detection
4. `src/main.py` — rewire the main loop (much simpler now)
5. Update `src/config.py` + `requirements.txt`
6. Deploy to VPS, test with cron

## Dependencies

- **Python:** `requests`, `python-dotenv`, `pytest`

## Risks

| Risk | Mitigation |
|------|-----------|
| PollEv blocks server IP | Unlikely for simple GET requests at 10s intervals. Can add random jitter if needed. |
| PollEv page structure changes | Log raw responses. Selectors/API may need updating between semesters. |
| Poll unlocks before script starts | Cron starts 5 min early. Heartbeat confirms it's running. |
| No active poll during class | Log "no poll found" — don't alert. Only alert on locked→unlocked. |

## Verification

1. `make test` — run pytest suite
2. Manual run: `python3 -m src.main` — confirm heartbeat + polling
3. Ask professor to unlock poll (or test during next class)
4. Verify cron: `crontab -l` on VPS
