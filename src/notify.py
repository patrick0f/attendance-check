import logging
import requests

logger = logging.getLogger(__name__)


class Notifier:
    def __init__(self, topic: str):
        self.url = f"https://ntfy.sh/{topic}"

    def _post(self, message: str, title: str, priority: str = "default", tags: str = ""):
        try:
            requests.post(
                self.url,
                data=message,
                headers={
                    "Title": title,
                    "Priority": priority,
                    "Tags": tags,
                },
            )
        except Exception:
            logger.exception("Failed to send notification")

    def send_alert(self, message: str):
        self._post(message, title="Attendance Check", priority="urgent", tags="warning")

    def send_heartbeat(self):
        self._post(
            "Script is running. Session is valid.",
            title="Attendance Check - Heartbeat",
            priority="default",
            tags="green_circle",
        )

    def send_error(self, message: str):
        self._post(
            message,
            title="Attendance Check - Error",
            priority="high",
            tags="rotating_light",
        )
