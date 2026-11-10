
"""Binary sensors for the VDL Parkings integration."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.entity import (
    DeviceInfo,
    EntityCategory,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, get_selected_parkings


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up parking status and API health binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for parking_id in get_selected_parkings(entry):
        parking_id = str(parking_id)

        if parking_id not in coordinator.data:
            continue

        parking_data = coordinator.data[parking_id]

        info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id, parking_id)},
            name=parking_data["name"],
            entry_type="service",
            manufacturer="VDL",
            model="Parking",
        )

        entities.extend(
            [
                ParkingOpen(coordinator, parking_id, info),
                ParkingFull(coordinator, parking_id, info),
                ParkingOutOfService(coordinator, parking_id, info),
            ]
        )

    health_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id, "api")},
        name="VDL Parkings API",
        manufacturer="Ville de Luxembourg",
        model="API diagnostics",
    )

    entities.append(ApiReachable(coordinator, health_info))

    async_add_entities(entities)


class ParkingBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Base class for parking status entities."""

    _attr_has_entity_name = True
    _attr_entity_registry_enabled_default = True

    def __init__(self, coordinator, parking_id, device_info):
        """Initialize the parking binary sensor."""
        super().__init__(coordinator)
        self.parking_id = parking_id
        self._device_info = device_info

    @property
    def device_info(self):
        """Return the associated parking device."""
        return self._device_info

    @property
    def extra_state_attributes(self):
        """Expose common parking metadata for dashboards and cards."""
        parking = self.coordinator.data[self.parking_id]

        return {
            "parking_id": str(self.parking_id),
            "parking_name": parking["name"],
            "last_updated": parking.get("last_updated"),
        }


class ParkingOpen(ParkingBinarySensor):
    """Whether the parking is open."""

    _attr_translation_key = "open"
    _attr_device_class = BinarySensorDeviceClass.OPENING

    @property
    def unique_id(self):
        return f"vdl_parking_{self.parking_id}_open"

    @property
    def is_on(self):
        return self.coordinator.data[self.parking_id]["open"]


class ParkingFull(ParkingBinarySensor):
    """Whether the parking is full."""

    _attr_translation_key = "full"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def unique_id(self):
        return f"vdl_parking_{self.parking_id}_full"

    @property
    def is_on(self):
        return self.coordinator.data[self.parking_id]["full"]


class ParkingOutOfService(ParkingBinarySensor):
    """Whether the parking is out of service."""

    _attr_translation_key = "out_of_service"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self):
        return f"vdl_parking_{self.parking_id}_out_of_service"

    @property
    def is_on(self):
        return self.coordinator.data[self.parking_id]["out_of_service"]


class ApiReachable(CoordinatorEntity, BinarySensorEntity):
    """Whether the most recent VDL API request succeeded."""

    _attr_name = "API reachable"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_has_entity_name = True

    def __init__(self, coordinator, device_info):
        """Initialize the API diagnostic binary sensor."""
        super().__init__(coordinator)
        self._device_info = device_info

    @property
    def device_info(self):
        return self._device_info

    @property
    def unique_id(self):
        return "vdl_parkings_api_reachable"

    @property
    def is_on(self):
        return self.coordinator.api_reachable

    @property
    def extra_state_attributes(self):
        return {
            "last_error": self.coordinator.last_error,
            "consecutive_failures": self.coordinator.consecutive_failures,
            "last_attempt": self.coordinator.last_attempt,
            "last_success": self.coordinator.last_success,
        }

