import time
import pytest
from src.checker import PollState
from src.detect import UnlockDetector


class TestUnlockDetector:
    def test_unlocked_from_no_previous_state_triggers(self):
        detector = UnlockDetector()
        assert detector.check(PollState.UNLOCKED) is True

    def test_locked_to_unlocked_triggers(self):
        detector = UnlockDetector()
        detector.check(PollState.LOCKED)
        assert detector.check(PollState.UNLOCKED) is True

    def test_no_poll_to_unlocked_triggers(self):
        detector = UnlockDetector()
        detector.check(PollState.NO_POLL)
        assert detector.check(PollState.UNLOCKED) is True

    def test_unlocked_to_unlocked_does_not_trigger(self):
        detector = UnlockDetector()
        detector.check(PollState.UNLOCKED)
        assert detector.check(PollState.UNLOCKED) is False

    def test_locked_does_not_trigger(self):
        detector = UnlockDetector()
        assert detector.check(PollState.LOCKED) is False

    def test_no_poll_does_not_trigger(self):
        detector = UnlockDetector()
        assert detector.check(PollState.NO_POLL) is False

    def test_error_does_not_trigger(self):
        detector = UnlockDetector()
        assert detector.check(PollState.ERROR) is False

    def test_relocked_then_unlocked_triggers_again(self):
        detector = UnlockDetector(cooldown_seconds=0)
        detector.check(PollState.UNLOCKED)
        detector.check(PollState.LOCKED)
        assert detector.check(PollState.UNLOCKED) is True

    def test_cooldown_suppresses_second_alert(self):
        detector = UnlockDetector(cooldown_seconds=180)
        assert detector.check(PollState.UNLOCKED) is True
        detector.check(PollState.LOCKED)
        assert detector.check(PollState.UNLOCKED) is False

    def test_cooldown_expires_allows_new_alert(self):
        detector = UnlockDetector(cooldown_seconds=1)
        assert detector.check(PollState.UNLOCKED) is True
        detector.check(PollState.LOCKED)
        time.sleep(1.1)
        assert detector.check(PollState.UNLOCKED) is True

    def test_multiple_no_poll_then_unlock(self):
        detector = UnlockDetector()
        detector.check(PollState.NO_POLL)
        detector.check(PollState.NO_POLL)
        detector.check(PollState.NO_POLL)
        assert detector.check(PollState.UNLOCKED) is True

    def test_error_to_unlocked_triggers(self):
        detector = UnlockDetector()
        detector.check(PollState.ERROR)
        assert detector.check(PollState.UNLOCKED) is True
