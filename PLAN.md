# Attendance Check Detector — Plan

## Context

Class is livestreamed via Panopto in the browser. Professor uses PollEv for attendance at unpredictable times. Goal: poll the livestream visually every ~10s and send a phone notification when PollEv appears on screen.

**Schedule:** Monday/Wednesday 2:30pm–3:45pm

## Approach: VPS + Playwright

Runs on a Linux VPS — no need to have your laptop open during class. A headless Playwright browser logs into Panopto, navigates to the livestream, and screenshots the video every 10 seconds. Tesseract OCR reads the frame, detection logic checks for PollEv, and ntfy.sh pushes to your phone.

**Tradeoff:** Duo 2FA means you can't fully automate login. You manually log in once via VNC (approve Duo on phone), and the session persists for days/weeks. Script detects expired sessions and notifies you to re-auth.

### Architecture

```
VPS (Ubuntu)
├── cron (starts at 2:25pm MW)
│   └── main.py
│       ├── Playwright (persistent browser context)
│       │   ├── checks if Panopto session is valid
│       │   ├── navigates to livestream URL
│       │   └── page.screenshot() every 10s
│       ├── Tesseract OCR → extract text from frame
│       ├── Detection logic → check for PollEv indicators
│       └── ntfy.sh → phone push notification
└── noVNC (web-based VNC for manual re-auth when needed)
```

### Components

#### 1. Browser Session (`src/browser.py`)
- **Playwright with persistent browser context** — cookies/session survive between runs
- On startup: navigate to Panopto livestream URL
- Check if redirected to SSO login page → if so, send "re-auth needed" notification and exit
- If session is valid: find the video player element, start screenshotting
- `page.screenshot()` — no OS-level screen capture needed, Playwright handles it natively

#### 2. OCR (`src/ocr.py`)
- **Tesseract** via `pytesseract` — standard Linux OCR, `apt-get install tesseract-ocr`
- Tesseract is plenty good for this use case: PollEv text is large, high-contrast, screen-rendered
- Preprocess: convert to grayscale, threshold for cleaner OCR if needed (Pillow)

#### 3. Detection (`src/detect.py`)
- Search OCR output for: `pollev`, `poll everywhere`, `pollev.com`
- **Require 2 consecutive detections** (20s) before alerting — prevents false positives
- Most testable component — TDD with sample OCR text

#### 4. Notification (`src/notify.py`)
- **ntfy.sh** — free, no account needed, single HTTP POST, has iOS/Android app
- Subscribe to a private topic like `attendance-check-<random>` on your phone
- 3-minute cooldown after alert to avoid spam
- Heartbeat notification at 2:26pm confirming "script is running, session is valid"
- "Re-auth needed" notification if session expired

#### 5. Main Loop (`src/main.py`)
```
1. Launch Playwright with persistent context
2. Navigate to Panopto livestream URL
3. If redirected to login → notify "re-auth needed", exit
4. Send heartbeat notification
5. Every 10 seconds:
   a. page.screenshot() → PIL Image
   b. Tesseract OCR → text
   c. Check for PollEv indicators
   d. If 2 consecutive detections + cooldown expired → send alert
   e. Log result
6. Exit after 3:45pm
```

#### 6. Scheduling
- **cron**: `25 14 * * 1,3  cd /path/to/project && python3 src/main.py`
- Starts 5 min early to handle navigation + session check
- Script exits itself after 3:45pm

#### 7. VNC for Re-Auth (`setup/vnc.md`)
- Install **noVNC** — browser-based VNC client, no app needed on your end
- When you get a "re-auth needed" notification:
  1. Open `http://your-vps:6080` in any browser
  2. Open Chromium, log into Panopto, approve Duo
  3. Close VNC — session cookies are now saved in the persistent context
- Re-auth frequency: depends on your university's session timeout (typically every 1-2 weeks)

### Config (`src/config.py`)
```python
CONFIG = {
    "poll_interval_seconds": 10,
    "alert_cooldown_seconds": 180,
    "consecutive_required": 2,
    "ntfy_topic": "attendance-check-CHANGEME",
    "panopto_livestream_url": "https://your-university.hosted.panopto.com/...",
    "class_end_time": "15:45",
    "timezone": "America/New_York",  # adjust to your timezone
}
```

## File Structure

```
attendance-check/
├── src/
│   ├── main.py            # entry point + main loop
│   ├── config.py          # settings
│   ├── browser.py         # Playwright session management
│   ├── ocr.py             # Tesseract OCR wrapper
│   ├── detect.py          # PollEv text detection
│   └── notify.py          # ntfy.sh integration
├── tests/
│   ├── test_detect.py     # detection logic tests (TDD)
│   ├── test_notify.py     # cooldown + notification tests
│   └── test_ocr.py        # OCR tests with sample images
├── setup/
│   ├── install.sh         # VPS setup script (deps, cron, vnc)
│   └── vnc.md             # re-auth instructions
├── Makefile               # test, run, deploy
├── requirements.txt       # playwright, pytesseract, Pillow, requests
└── samples/               # sample screenshots for testing
```

## Implementation Order

1. `src/detect.py` + `tests/test_detect.py` — TDD the detection logic first (no infra needed)
2. `src/ocr.py` + `tests/test_ocr.py` — Tesseract wrapper, test with sample screenshots
3. `src/notify.py` + `tests/test_notify.py` — ntfy integration + cooldown logic
4. `src/browser.py` — Playwright persistent context, session check, screenshot capture
5. `src/main.py` — wire everything together
6. `setup/install.sh` — VPS provisioning script (apt deps, cron, noVNC)
7. Deploy to VPS, manual login via VNC, end-to-end test

## Dependencies

- **Python:** `playwright`, `pytesseract`, `Pillow`, `requests`
- **System (apt):** `tesseract-ocr`, `chromium-browser`, `novnc`, `x11vnc`, `xvfb`
- **Phone:** ntfy app (free)
- **VPS:** Any cheap Ubuntu VPS (~$5/month — DigitalOcean, Hetzner, etc.)

## Risks

| Risk | Mitigation |
|------|-----------|
| Duo session expires mid-class | Check session validity at startup (2:25pm). If expired, send "re-auth needed" alert immediately — you have 5 min before class. |
| Panopto livestream URL changes | Config file. Could also auto-discover from Panopto course page if needed. |
| OCR misreads | Multiple indicators + 2 consecutive frames. Log all OCR text for tuning. |
| Tesseract quality | PollEv text is large + high-contrast — Tesseract handles this well. Grayscale preprocessing helps. |
| VPS goes down | ntfy heartbeat at 2:26pm. No heartbeat = something's wrong. |
| Playwright breaks on Panopto | Panopto is a standard web app. Persistent context avoids re-login complexity. |

## VPS Setup Checklist

1. Spin up Ubuntu VPS ($5/month tier)
2. Run `setup/install.sh` (installs Python, Tesseract, Chromium, noVNC, Xvfb)
3. Clone repo, `pip install -r requirements.txt`, `playwright install chromium`
4. Open noVNC in browser, launch Chromium, log into Panopto (approve Duo)
5. Update `src/config.py` with your ntfy topic + Panopto URL
6. `make install-cron` to set up the schedule
7. Wait for next class — check for heartbeat notification at 2:26pm

## Verification

1. `make test` — runs pytest suite locally
2. `make run` — manual run for testing (works locally or on VPS)
3. Deploy to VPS, trigger manual run, confirm heartbeat + screenshot capture
4. Open a Panopto recording containing PollEv → confirm detection + phone notification
5. Verify cron with `crontab -l` on VPS



 Step 4: Push code to the VPS

  # From your laptop
  scp -r /Users/p/Documents/GitHub/attendance-check root@<VPS_IP>:/root/attendance-check

  Or push to GitHub and clone on the VPS — either works.

  Step 5: SSH in and run setup

  ssh root@<VPS_IP>
  cd /root/attendance-check
  chmod +x setup/install.sh
  ./setup/install.sh

  This installs Python, Tesseract, Chromium, Xvfb, noVNC, and sets up the Python venv.

  Step 6: Start the virtual display + VNC

  # Start virtual display
  Xvfb :99 -screen 0 1280x720x24 &
  export DISPLAY=:99

  # Start VNC server
  x11vnc -display :99 -forever -nopw &

  # Start noVNC (web-based VNC)
  /usr/share/novnc/utils/launch.sh --listen 6080 --vnc localhost:5900 &

  Step 7: Log into Panopto via VNC (one-time)

  - Open http://<VPS_IP>:6080 in your browser (any device)
  - You'll see a remote desktop
  - Open Chromium in the VNC session
  - Navigate to your Panopto URL
  - Log in with your university credentials
  - Approve Duo on your phone
  - Once you see the Panopto page, close Chromium
  - Close the noVNC browser tab
  - Session cookies are now saved in .browser_data/

  Step 8: Test it manually

  ssh root@<VPS_IP>
  cd /root/attendance-check
  source .venv/bin/activate
  DISPLAY=:99 python3 -m src.main

  You should see:
  1. A heartbeat notification on your phone
  2. Log output showing OCR running every 10 seconds
  3. Ctrl+C to stop

  Step 9: Install the cron job

  make install-cron
  crontab -l  # verify it shows the MW 2:25pm entry

  Step 10: Verify on a real class day

  - Monday or Wednesday, check your phone at ~2:26pm
  - You should get the heartbeat notification ("Script is running. Session is valid.")
  - If you get "Re-Auth Needed" instead, open the VNC page and redo step 7

  Ongoing maintenance

  - If you get "Re-Auth Needed": Redo step 7 (takes ~1 minute)
  - If you get no heartbeat: SSH in and check the log at /var/log/attendance-check.log
  - If the Panopto URL changes: Update src/config.py and re-deploy