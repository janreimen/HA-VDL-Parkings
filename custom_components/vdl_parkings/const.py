"""Constants for VDL Parkings."""

DOMAIN = "vdl_parkings"
CONF_PARKINGS = "parkings"
CONF_ZONES_MAPPING = "zones_mapping"
CONF_LANGUAGE = "language"
CONF_PARKING_SCHEDULES = "parking_schedules"
CONF_HIGH_INTERVAL = "high_interval"
CONF_LOW_INTERVAL = "low_interval"
CONF_DAY_START = "day_start"
CONF_NIGHT_START = "night_start"

DEFAULT_HIGH_INTERVAL = 60
DEFAULT_LOW_INTERVAL = 600
DEFAULT_DAY_START = "06:00"
DEFAULT_NIGHT_START = "23:00"
SCHEDULER_TICK_SECONDS = 30

LANGUAGES = {"lu": "Lëtzebuergesch", "de": "Deutsch", "fr": "Français", "en": "English"}
