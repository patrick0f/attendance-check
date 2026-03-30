import logging
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
load_dotenv()

from playwright.sync_api import sync_playwright

from src.browser import create_context, navigate_to_stream, take_screenshot
from src.config import CONFIG
from src.detect import PollEvDetector
from src.notify import Notifier
from src.ocr import extract_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

SCREENSHOT_PATH = "/tmp/attendance_frame.png"


def past_end_time() -> bool:
    tz = ZoneInfo(CONFIG["timezone"])
    now = datetime.now(tz)
    h, m = map(int, CONFIG["class_end_time"].split(":"))
    return now.hour > h or (now.hour == h and now.minute >= m)


def main():
    notifier = Notifier(topic=CONFIG["ntfy_topic"])
    detector = PollEvDetector(
        consecutive_required=CONFIG["consecutive_required"],
        cooldown_seconds=CONFIG["alert_cooldown_seconds"],
    )

    with sync_playwright() as pw:
        context = create_context(pw)
        page = context.new_page()

        logger.info("Navigating to %s", CONFIG["panopto_folder_url"])
        session_valid = navigate_to_stream(page, CONFIG["panopto_folder_url"])

        if not session_valid:
            logger.error("Session expired — sending re-auth notification")
            notifier.send_reauth_needed()
            context.close()
            return

        notifier.send_heartbeat()
        logger.info("Session valid. Starting poll loop.")

        while not past_end_time():
            try:
                take_screenshot(page, SCREENSHOT_PATH)
                ocr_text = extract_text(SCREENSHOT_PATH)
                logger.info("OCR extracted %d chars", len(ocr_text))

                if detector.check(ocr_text):
                    logger.info("PollEv detected! Sending alert.")
                    notifier.send_alert("PollEv detected! Check your class now.")
            except Exception:
                logger.exception("Error in poll loop")

            time.sleep(CONFIG["poll_interval_seconds"])

        logger.info("Class ended. Shutting down.")
        context.close()


if __name__ == "__main__":
    main()
