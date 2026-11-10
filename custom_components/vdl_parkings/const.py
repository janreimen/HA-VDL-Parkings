
"""Constants for VDL Parkings."""

DOMAIN = "vdl_parkings"

# Configuration keys
CONF_PARKINGS = "parkings"
CONF_ZONES_MAPPING = "zones_mapping"
CONF_LANGUAGE = "language"
CONF_PARKING_SCHEDULES = "parking_schedules"

# Per-parking polling schedule keys
CONF_HIGH_INTERVAL = "high_interval"
CONF_LOW_INTERVAL = "low_interval"
CONF_DAY_START = "day_start"
CONF_NIGHT_START = "night_start"

# Default polling configuration
DEFAULT_HIGH_INTERVAL = 60
DEFAULT_LOW_INTERVAL = 600

DEFAULT_DAY_START = "06:00"
DEFAULT_NIGHT_START = "23:00"

# Scheduler execution frequency.
# The coordinator checks every 30 seconds whether any parking is due.
SCHEDULER_TICK_SECONDS = 30

# Integration configuration version
CONFIG_VERSION = 3

# Supported UI languages
LANGUAGES = {
    "lu": "Lëtzebuergesch",
    "de": "Deutsch",
    "fr": "Français",
    "en": "English",
}


def get_selected_parkings(entry):
    """Return selected parking IDs, supporting existing config entries."""
    return entry.options.get(
        CONF_PARKINGS,
        entry.data.get(CONF_PARKINGS, []),
    )


def get_parking_schedules(entry):
    """Return parking schedules, supporting existing config entries."""
    return entry.options.get(
        CONF_PARKING_SCHEDULES,
        entry.data.get(CONF_PARKING_SCHEDULES, {}),
    )


def get_language(entry):
    """Return the configured UI language."""
    return entry.options.get(
        CONF_LANGUAGE,
        entry.data.get(CONF_LANGUAGE, "en"),
    )

