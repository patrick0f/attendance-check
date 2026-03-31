import logging
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
load_dotenv()

from playwright.sync_api import sync_playwright

from src.checker import PollEvChecker
from src.config import CONFIG
from src.detect import UnlockDetector
from src.notify import Notifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def past_end_time() -> bool:
    tz = ZoneInfo(CONFIG["timezone"])
    now = datetime.now(tz)
    h, m = map(int, CONFIG["class_end_time"].split(":"))
    return now.hour > h or (now.hour == h and now.minute >= m)


def main():
    notifier = Notifier(topic=CONFIG["ntfy_topic"])
    detector = UnlockDetector(cooldown_seconds=CONFIG["alert_cooldown_seconds"])
    checker = PollEvChecker(pollev_url=CONFIG["pollev_url"])

    with sync_playwright() as pw:
        checker.start(pw)
        notifier.send_heartbeat()
        logger.info("Browser started. Polling %s every %ds.",
                     CONFIG["pollev_url"], CONFIG["poll_interval_seconds"])

        while not past_end_time():
            try:
                state = checker.check()
                logger.info("Poll state: %s", state.value)

                if detector.check(state):
                    logger.info("Poll unlocked! Sending alert.")
                    notifier.send_alert("PollEv is unlocked! Respond now.")
            except Exception:
                logger.exception("Error in poll loop")

            time.sleep(CONFIG["poll_interval_seconds"])

        logger.info("Class ended. Shutting down.")
        checker.stop()


if __name__ == "__main__":
    main()
