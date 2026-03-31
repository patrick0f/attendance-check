import os

CONFIG = {
    "poll_interval_seconds": 10,
    "alert_cooldown_seconds": 180,
    "ntfy_topic": os.environ.get("NTFY_TOPIC", "CHANGEME"),
    "pollev_url": os.environ.get("POLLEV_URL", ""),
    "class_end_time": "15:45",
    "timezone": "America/New_York",
}
