import logging
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

logger = logging.getLogger(__name__)

USER_DATA_DIR = Path(__file__).parent.parent / ".browser_data"


def create_context(playwright) -> BrowserContext:
    return playwright.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=True,
        args=["--disable-blink-features=AutomationControlled"],
    )


def is_login_page(url: str) -> bool:
    lower = url.lower()
    return "shibboleth" in lower or "login" in lower or "cas" in lower


def navigate_to_folder(page: Page, folder_url: str) -> bool:
    page.goto(folder_url, wait_until="networkidle", timeout=30000)
    if is_login_page(page.url):
        logger.warning("Redirected to login page: %s", page.url)
        return False
    return True


def find_live_session(page: Page) -> bool:
    # Panopto marks live sessions with a "LIVE" badge or "Broadcasting" status.
    # Try multiple selectors that Panopto uses for live indicators.
    live_selectors = [
        "a:has-text('LIVE')",
        ".live-indicator",
        "[class*='live']",
        "a:has-text('Broadcasting')",
        ".session-row:has(.live)",
    ]

    for selector in live_selectors:
        try:
            element = page.locator(selector).first
            if element.is_visible(timeout=2000):
                logger.info("Found live session via selector: %s", selector)
                element.click()
                page.wait_for_load_state("networkidle", timeout=15000)
                return True
        except Exception:
            continue

    # Fallback: click the most recent session (top of the list).
    # During class time, this is almost always the active livestream.
    try:
        first_session = page.locator(".session-row a, .detail-title a").first
        if first_session.is_visible(timeout=3000):
            logger.info("No live badge found. Clicking most recent session as fallback.")
            first_session.click()
            page.wait_for_load_state("networkidle", timeout=15000)
            return True
    except Exception:
        pass

    logger.warning("Could not find any session to open")
    return False


def navigate_to_stream(page: Page, folder_url: str) -> bool:
    if not navigate_to_folder(page, folder_url):
        return False
    return find_live_session(page)


def take_screenshot(page: Page, path: str) -> str:
    page.screenshot(path=path)
    return path
