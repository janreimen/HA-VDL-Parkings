
"""Support for VDL Parkings zones."""

import logging

from homeassistant.components.zone import ZoneStorageCollection
from homeassistant.helpers.collection import ItemNotFound

from .const import (
    CONF_ZONES_MAPPING,
    get_selected_parkings,
)

_LOGGER = logging.getLogger(__name__)


async def create_parking_zones(hass, coordinator, entry):
    """Create and maintain zones for selected parkings.

    Existing zones are reused when their coordinates match. Zones belonging
    to parkings removed from the configuration are deleted.
    """
    zone_collection: ZoneStorageCollection = (
        hass.data["zone"].storage_collection
    )

    selected = [
        str(parking_id)
        for parking_id in get_selected_parkings(entry)
    ]

    zones_mapping = {
        str(parking_id): zone_id
        for parking_id, zone_id in entry.data.get(
            CONF_ZONES_MAPPING,
            {},
        ).items()
    }

    new_mapping = {}

    # Keep a snapshot of existing zones for coordinate deduplication.
    all_zones = zone_collection.async_items()

    for parking_id in selected:
        parking = coordinator.data.get(parking_id)

        if not parking:
            _LOGGER.warning(
                "No coordinator data available for parking '%s'; "
                "skipping zone creation",
                parking_id,
            )
            continue

        latitude = parking.get("latitude")
        longitude = parking.get("longitude")

        if latitude is None or longitude is None:
            _LOGGER.debug(
                "Parking '%s' has no coordinates; skipping zone creation",
                parking_id,
            )
            continue

        # First check whether this integration already tracks a zone
        # for the parking.
        zone_id = zones_mapping.get(parking_id)
        zone_exists = False

        if zone_id:
            for zone in all_zones:
                if zone["id"] != zone_id:
                    continue

                if (
                    zone.get("latitude") == latitude
                    and zone.get("longitude") == longitude
                ):
                    zone_exists = True
                    new_mapping[parking_id] = zone_id

                    _LOGGER.debug(
                        "Zone '%s' already exists for parking '%s' "
                        "with matching coordinates",
                        zone_id,
                        parking_id,
                    )
                else:
                    try:
                        await zone_collection.async_delete_item(zone_id)
                    except ItemNotFound:
                        pass

                    _LOGGER.info(
                        "Coordinates changed for parking '%s'; "
                        "deleted old zone '%s'",
                        parking_id,
                        zone_id,
                    )

                break

        if zone_exists:
            continue

        # Reuse an existing parking zone with matching coordinates
        # before creating a new one.
        zone_id = None

        for zone in all_zones:
            if (
                zone.get("latitude") == latitude
                and zone.get("longitude") == longitude
                and zone.get("icon") == "mdi:parking"
                and "Parking" in zone.get("name", "")
            ):
                zone_id = zone["id"]

                _LOGGER.debug(
                    "Found existing zone '%s' with matching coordinates "
                    "for parking '%s'; reusing it",
                    zone_id,
                    parking_id,
                )
                break

        if zone_id is None:
            zone = await zone_collection.async_create_item(
                {
                    "name": f"Parking {parking['name']}",
                    "latitude": latitude,
                    "longitude": longitude,
                    "radius": 100,
                    "icon": "mdi:parking",
                }
            )

            zone_id = zone["id"]

            _LOGGER.info(
                "Created new zone '%s' for parking '%s' "
                "and config entry %s",
                zone_id,
                parking_id,
                entry.entry_id,
            )

        new_mapping[parking_id] = zone_id

    # Remove zones previously tracked by this integration for parkings
    # that are no longer selected.
    for parking_id, zone_id in zones_mapping.items():
        if parking_id in selected:
            continue

        try:
            await zone_collection.async_delete_item(zone_id)
            _LOGGER.info(
                "Deleted zone '%s' for deselected parking '%s'",
                zone_id,
                parking_id,
            )
        except ItemNotFound:
            _LOGGER.debug(
                "Zone '%s' for deselected parking '%s' no longer exists",
                zone_id,
                parking_id,
            )

    # Persist the mapping while preserving all other entry data.
    if new_mapping != zones_mapping:
        hass.config_entries.async_update_entry(
            entry,
            data={
                **entry.data,
                CONF_ZONES_MAPPING: new_mapping,
            },
        )

    _LOGGER.debug(
        "Updated %d parking zone mappings for entry %s: %s",
        len(new_mapping),
        entry.entry_id,
        new_mapping,
    )


async def remove_parking_zones(hass, entry):
    """Remove zones tracked by this integration when it is unloaded."""
    zone_collection: ZoneStorageCollection = (
        hass.data["zone"].storage_collection
    )

    zones_mapping = entry.data.get(CONF_ZONES_MAPPING, {})

    for zone_id in zones_mapping.values():
        try:
            await zone_collection.async_delete_item(zone_id)

            _LOGGER.info(
                "Deleted zone '%s' from config entry %s",
                zone_id,
                entry.entry_id,
            )
        except ItemNotFound:
            _LOGGER.debug(
                "Zone '%s' from config entry %s no longer exists",
                zone_id,
                entry.entry_id,
            )

    _LOGGER.debug(
        "Removed %d tracked zones from entry %s: %s",
        len(zones_mapping),
        entry.entry_id,
        list(zones_mapping.values()),
    )

