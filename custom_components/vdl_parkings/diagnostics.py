
"""Diagnostics support for VDL Parkings."""

from homeassistant.components.diagnostics import async_redact_data

from .const import (
    CONF_LANGUAGE,
    CONF_PARKINGS,
    CONF_PARKING_SCHEDULES,
    CONF_ZONES_MAPPING,
    DOMAIN,
)

TO_REDACT = {
    "latitude",
    "longitude",
}


async def async_get_config_entry_diagnostics(hass, entry):
    """Return diagnostic information for a config entry."""
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)

    if coordinator is None:
        return {
            "entry": {
                "version": entry.version,
                "minor_version": entry.minor_version,
                "data": {
                    "selected_parkings": entry.options.get(
                        CONF_PARKINGS,
                        entry.data.get(CONF_PARKINGS, []),
                    ),
                    "language": entry.options.get(
                        CONF_LANGUAGE,
                        entry.data.get(CONF_LANGUAGE, "en"),
                    ),
                },
            },
            "coordinator": None,
        }

    parking_data = {
        parking_id: {
            key: value
            for key, value in parking.items()
            if key not in TO_REDACT
        }
        for parking_id, parking in coordinator.data.items()
    }

    schedules = entry.options.get(
        CONF_PARKING_SCHEDULES,
        entry.data.get(CONF_PARKING_SCHEDULES, {}),
    )

    return {
        "entry": {
            "version": entry.version,
            "minor_version": entry.minor_version,
            "data": {
                "selected_parkings": entry.options.get(
                    CONF_PARKINGS,
                    entry.data.get(CONF_PARKINGS, []),
                ),
                "language": entry.options.get(
                    CONF_LANGUAGE,
                    entry.data.get(CONF_LANGUAGE, "en"),
                ),
                "parking_schedules": schedules,
                "zones_mapping": entry.data.get(
                    CONF_ZONES_MAPPING,
                    {},
                ),
            },
        },
        "coordinator": {
            "health": coordinator.health,
            "selected_parkings": sorted(coordinator.selected),
            "parking_data": parking_data,
        },
    }

