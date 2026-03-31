import pytest
from src.checker import PollState, parse_poll_state


class TestParsePollState:
    def test_no_poll_activity_not_found(self):
        text = "Activity not found"
        assert parse_poll_state(text) == PollState.NO_POLL

    def test_no_poll_waiting_for_presenter(self):
        text = "Waiting for the presenter to activate a poll"
        assert parse_poll_state(text) == PollState.NO_POLL

    def test_no_poll_no_active_activities(self):
        text = "There are no active activities"
        assert parse_poll_state(text) == PollState.NO_POLL

    def test_locked_poll_with_lock_indicator(self):
        text = "What is AI? Responses are locked Submit"
        assert parse_poll_state(text) == PollState.LOCKED

    def test_locked_poll_waiting_to_open(self):
        text = "What is AI? Waiting for responses to open"
        assert parse_poll_state(text) == PollState.LOCKED

    def test_unlocked_poll_with_submit(self):
        text = "What is AI? A) Yes B) No C) Maybe Submit your response"
        assert parse_poll_state(text) == PollState.UNLOCKED

    def test_unlocked_poll_with_respond(self):
        text = "What is AI? Respond now Type your answer"
        assert parse_poll_state(text) == PollState.UNLOCKED

    def test_empty_text_is_error(self):
        assert parse_poll_state("") == PollState.ERROR

    def test_unrecognized_text_is_error(self):
        assert parse_poll_state("some random page content") == PollState.ERROR

    def test_case_insensitive_activity_not_found(self):
        text = "ACTIVITY NOT FOUND"
        assert parse_poll_state(text) == PollState.NO_POLL

    def test_case_insensitive_locked(self):
        text = "Question 1 RESPONSES ARE LOCKED"
        assert parse_poll_state(text) == PollState.LOCKED

    def test_unlocked_with_type_your_answer(self):
        text = "What year was it founded? Type your answer here"
        assert parse_poll_state(text) == PollState.UNLOCKED
