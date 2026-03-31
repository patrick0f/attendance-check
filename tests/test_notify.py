import pytest
from unittest.mock import patch, MagicMock
from src.notify import Notifier


class TestNotifier:
    def test_send_alert_posts_to_ntfy(self):
        notifier = Notifier(topic="test-topic")
        with patch("src.notify.requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            notifier.send_alert("PollEv detected!")
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            assert args[0] == "https://ntfy.sh/test-topic"
            assert kwargs["data"] == "PollEv detected!"
            assert kwargs["headers"]["Priority"] == "urgent"

    def test_send_heartbeat_posts_with_low_priority(self):
        notifier = Notifier(topic="test-topic")
        with patch("src.notify.requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            notifier.send_heartbeat()
            args, kwargs = mock_post.call_args
            assert kwargs["headers"]["Priority"] == "default"

    def test_send_error(self):
        notifier = Notifier(topic="test-topic")
        with patch("src.notify.requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            notifier.send_error("Browser crashed")
            args, kwargs = mock_post.call_args
            assert kwargs["data"] == "Browser crashed"
            assert kwargs["headers"]["Priority"] == "high"

    def test_send_alert_handles_network_error(self):
        notifier = Notifier(topic="test-topic")
        with patch("src.notify.requests.post", side_effect=Exception("network error")):
            notifier.send_alert("test")  # should not raise
