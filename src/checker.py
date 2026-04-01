import logging
from enum import Enum

logger = logging.getLogger(__name__)


class PollState(Enum):
    NO_POLL = "no_poll"
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    ERROR = "error"


NO_POLL_INDICATORS = [
    "activity not found",
    "waiting for the presenter",
    "no active activities",
    "presentation to begin",
    "presentation is underway",
]

LOCKED_INDICATORS = [
    "this poll is locked",
    "responses are locked",
    "waiting for responses to open",
    "\nlocked\n",
    "\nlocked",
]

UNLOCKED_INDICATORS = [
    "submit your response",
    "respond now",
    "type your answer",
    "type your response",
    "you may respond",
    "you can respond",
    "tap to respond",
    "click to respond",
    "drag to rank",
    "click on the image",
    "submit",
    "responding as",
]


def parse_poll_state(page_text: str) -> PollState:
    """Determine poll state from the visible text of the PollEv page."""
    text = page_text.lower().strip()

    if not text:
        return PollState.ERROR

    for indicator in NO_POLL_INDICATORS:
        if indicator in text:
            return PollState.NO_POLL

    for indicator in LOCKED_INDICATORS:
        if indicator in text:
            return PollState.LOCKED

    for indicator in UNLOCKED_INDICATORS:
        if indicator in text:
            return PollState.UNLOCKED

    return PollState.ERROR


class PollEvChecker:
    """Manages a Playwright browser and checks PollEv poll state."""

    def __init__(self, pollev_url: str):
        self.pollev_url = pollev_url
        self._page = None
        self._browser = None
        self._playwright = None

    def _dismiss_dialogs(self):
        """Click through cookie banner and name prompt if present."""
        try:
            accept_btn = self._page.get_by_role("button", name="Agree")
            if accept_btn.is_visible(timeout=3000):
                accept_btn.click()
                logger.info("Dismissed cookie banner")
                self._page.wait_for_timeout(1000)
        except Exception:
            pass

        try:
            skip_btn = self._page.get_by_text("skip", exact=False)
            if skip_btn.is_visible(timeout=3000):
                skip_btn.click()
                logger.info("Clicked skip name prompt")
                self._page.wait_for_timeout(1000)
        except Exception:
            pass

    def start(self, playwright):
        """Launch browser and navigate to PollEv page."""
        self._playwright = playwright
        self._browser = playwright.chromium.launch(headless=True)
        self._page = self._browser.new_page()
        logger.info("Navigating to %s", self.pollev_url)
        self._page.goto(self.pollev_url, wait_until="domcontentloaded", timeout=30000)
        self._page.wait_for_timeout(3000)
        self._dismiss_dialogs()

    def check(self) -> PollState:
        """Reload and return current poll state."""
        try:
            self._page.reload(wait_until="domcontentloaded", timeout=30000)
            self._page.wait_for_timeout(3000)
            text = self._page.inner_text("body")
            logger.info("Page text (%d chars): %.500s", len(text), text)
            return parse_poll_state(text)
        except Exception:
            logger.exception("Error checking poll state")
            return PollState.ERROR

    def stop(self):
        """Close browser."""
        if self._browser:
            self._browser.close()
