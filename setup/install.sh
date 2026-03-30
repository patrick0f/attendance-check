#!/usr/bin/env bash
set -euo pipefail

echo "=== Attendance Check — VPS Setup ==="

# System deps
sudo apt-get update
sudo apt-get install -y \
    python3 python3-pip python3-venv \
    tesseract-ocr \
    xvfb x11vnc novnc \
    chromium-browser

# Python environment
cd "$(dirname "$0")/.."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Create browser data directory
mkdir -p .browser_data

# Xvfb display (add to ~/.bashrc or systemd)
echo ""
echo "=== Manual steps remaining ==="
echo "1. Start virtual display:  Xvfb :99 -screen 0 1280x720x24 &"
echo "2. Export display:         export DISPLAY=:99"
echo "3. Start noVNC:            /usr/share/novnc/utils/launch.sh --listen 6080 --vnc localhost:5900 &"
echo "4. Start x11vnc:           x11vnc -display :99 -forever -nopw &"
echo "5. Open http://<your-vps-ip>:6080 in a browser"
echo "6. In the VNC session, open Chromium and log into Panopto (approve Duo)"
echo "7. Close Chromium — cookies are saved in .browser_data/"
echo "8. Install cron:           make install-cron"
