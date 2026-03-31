import time

from src.checker import PollState


class UnlockDetector:
    """Detects locked → unlocked transitions with cooldown."""

    def __init__(self, cooldown_seconds: int = 180):
        self.cooldown_seconds = cooldown_seconds
        self._prev_state: PollState | None = None
        self._last_alert_time: float | None = None

    def check(self, state: PollState) -> bool:
        """Return True if we should alert (poll just unlocked)."""
        should_alert = False

        if state == PollState.UNLOCKED and self._prev_state != PollState.UNLOCKED:
            if self._last_alert_time is None or (
                time.time() - self._last_alert_time >= self.cooldown_seconds
            ):
                should_alert = True
                self._last_alert_time = time.time()

        self._prev_state = state
        return should_alert
