
"""The VDL Parkings integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_LANGUAGE,
    CONF_PARKING_SCHEDULES,
    CONF_PARKINGS,
    CONFIG_VERSION,
    DEFAULT_HIGH_INTERVAL,
    DEFAULT_LOW_INTERVAL,
    DEFAULT_DAY_START,
    DEFAULT_NIGHT_START,
    DOMAIN,
)
from .coordinator import VdlParkingCoordinator
from .zone import create_parking_zones, remove_parking_zones

PLATFORMS = ["binary_sensor", "sensor"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up VDL Parkings from a config entry."""
    coordinator = VdlParkingCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await create_parking_zones(hass, coordinator, entry)

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload the integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        await remove_parking_zones(hass, entry)
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)

    return unload_ok


async def async_migrate_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Migrate older config entries to the current configuration version."""
    if entry.version >= CONFIG_VERSION:
        return True

    data = dict(entry.data)
    options = dict(entry.options)

    # Preserve the selected parking IDs from older configurations.
    selected = options.get(
        CONF_PARKINGS,
        data.get(CONF_PARKINGS, []),
    )

    # Preserve schedules regardless of whether they were previously
    # stored in config-entry data or options.
    schedules = options.get(
        CONF_PARKING_SCHEDULES,
        data.get(CONF_PARKING_SCHEDULES, {}),
    )

    language = options.get(
        CONF_LANGUAGE,
        data.get(CONF_LANGUAGE, "en"),
    )

    # Ensure every selected parking has a complete default schedule.
    normalized_schedules = {}

    for parking_id in selected:
        previous = schedules.get(str(parking_id), {})
        normalized_schedules[str(parking_id)] = {
            "high_interval": previous.get(
                "high_interval",
                DEFAULT_HIGH_INTERVAL,
            ),
            "low_interval": previous.get(
                "low_interval",
                DEFAULT_LOW_INTERVAL,
            ),
            "day_start": previous.get(
                "day_start",
                DEFAULT_DAY_START,
            ),
            "night_start": previous.get(
                "night_start",
                DEFAULT_NIGHT_START,
            ),
        }

    # Keep the original data fields, including zone mappings.
    # Store the normalized configuration in options so that the
    # integration can consistently read the current configuration.
    options.update(
        {
            CONF_PARKINGS: list(selected),
            CONF_LANGUAGE: language,
            CONF_PARKING_SCHEDULES: normalized_schedules,
        }
    )

    hass.config_entries.async_update_entry(
        entry,
        options=options,
        version=CONFIG_VERSION,
    )

    return True

