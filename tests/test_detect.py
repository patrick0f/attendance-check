import pytest
from src.detect import detect_pollev, PollEvDetector


class TestDetectPollev:
    def test_detects_pollev_lowercase(self):
        detected, matches = detect_pollev("welcome to pollev click here")
        assert detected is True
        assert "pollev" in matches

    def test_detects_poll_everywhere(self):
        detected, matches = detect_pollev("Open Poll Everywhere to respond")
        assert detected is True
        assert "poll everywhere" in matches

    def test_detects_pollev_dot_com(self):
        detected, matches = detect_pollev("Go to PollEv.com/professor123")
        assert detected is True
        assert "pollev.com" in matches

    def test_no_match_on_unrelated_text(self):
        detected, matches = detect_pollev("Today we will discuss regression analysis")
        assert detected is False
        assert matches == []

    def test_no_match_on_empty_string(self):
        detected, matches = detect_pollev("")
        assert detected is False
        assert matches == []

    def test_no_match_on_partial_words(self):
        detected, matches = detect_pollev("the polls are everywhere today")
        assert detected is False
        assert matches == []

    def test_case_insensitive(self):
        detected, _ = detect_pollev("POLLEV IS NOW OPEN")
        assert detected is True

    def test_mixed_case_poll_everywhere(self):
        detected, _ = detect_pollev("Poll everywhere is active")
        assert detected is True

    def test_multiple_indicators(self):
        detected, matches = detect_pollev("Go to PollEv.com - Poll Everywhere is open")
        assert detected is True
        assert len(matches) >= 2

    def test_ocr_noise_no_false_positive(self):
        detected, _ = detect_pollev("p0llev pollen polled polling")
        assert detected is False

    def test_realistic_ocr_output_with_pollev(self):
        ocr_text = """
        Lecture 12: Market Equilibrium
        PollEv.com/smithj
        Question 1: What is the equilibrium price?
        A) $10  B) $15  C) $20  D) $25
        """
        detected, matches = detect_pollev(ocr_text)
        assert detected is True

    def test_realistic_ocr_output_without_pollev(self):
        ocr_text = """
        Lecture 12: Market Equilibrium
        Supply and Demand Curves
        Price elasticity of demand
        Consumer surplus = area above price, below demand
        """
        detected, _ = detect_pollev(ocr_text)
        assert detected is False


class TestPollEvDetector:
    def test_single_detection_does_not_trigger(self):
        detector = PollEvDetector(consecutive_required=2)
        assert detector.check("pollev is open") is False

    def test_two_consecutive_detections_triggers(self):
        detector = PollEvDetector(consecutive_required=2)
        detector.check("pollev is open")
        assert detector.check("pollev is open") is True

    def test_gap_resets_consecutive_count(self):
        detector = PollEvDetector(consecutive_required=2)
        detector.check("pollev is open")
        detector.check("normal lecture slide")
        assert detector.check("pollev is open") is False

    def test_three_required_consecutive(self):
        detector = PollEvDetector(consecutive_required=3)
        detector.check("pollev is open")
        detector.check("pollev is open")
        assert detector.check("pollev is open") is True

    def test_cooldown_suppresses_repeated_alerts(self):
        detector = PollEvDetector(consecutive_required=1, cooldown_seconds=180)
        assert detector.check("pollev is open") is True
        assert detector.check("pollev is open") is False

    def test_cooldown_expires(self):
        detector = PollEvDetector(consecutive_required=1, cooldown_seconds=1)
        assert detector.check("pollev is open") is True
        import time
        time.sleep(1.1)
        assert detector.check("pollev is open") is True
