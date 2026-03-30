import os

CONFIG = {
    "poll_interval_seconds": 10,
    "alert_cooldown_seconds": 180,
    "consecutive_required": 2,
    "ntfy_topic": os.environ.get("NTFY_TOPIC", "CHANGEME"),
    "panopto_folder_url": os.environ.get("PANOPTO_FOLDER_URL", ""),
    "class_end_time": "15:45",
    "timezone": "America/New_York",
}
