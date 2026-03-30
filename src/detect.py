import time

STRONG_INDICATORS = ["pollev", "poll everywhere", "pollev.com"]


def detect_pollev(ocr_text: str) -> tuple[bool, list[str]]:
    text_lower = ocr_text.lower()
    matches = [ind for ind in STRONG_INDICATORS if ind in text_lower]
    detected = len(matches) > 0
    return (detected, matches)


class PollEvDetector:
    def __init__(self, consecutive_required: int = 2, cooldown_seconds: int = 180):
        self.consecutive_required = consecutive_required
        self.cooldown_seconds = cooldown_seconds
        self._consecutive = 0
        self._last_alert_time: float | None = None

    def check(self, ocr_text: str) -> bool:
        detected, _ = detect_pollev(ocr_text)

        if detected:
            self._consecutive += 1
        else:
            self._consecutive = 0
            return False

        if self._consecutive < self.consecutive_required:
            return False

        if self._last_alert_time is not None:
            elapsed = time.time() - self._last_alert_time
            if elapsed < self.cooldown_seconds:
                return False

        self._last_alert_time = time.time()
        return True
