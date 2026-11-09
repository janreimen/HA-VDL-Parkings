"""Sensors for VDL Parkings integration."""

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_PARKINGS


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up parking and integration diagnostic sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for parking_id in entry.data[CONF_PARKINGS]:
        if parking_id not in coordinator.data:
            continue
        info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id, parking_id)},
            name=coordinator.data[parking_id]["name"],
            entry_type="service", manufacturer="VDL", model="Parking",
        )
        entities.extend([
            ParkingAvailableSpaces(coordinator, parking_id, info),
            ParkingTotalCapacity(coordinator, parking_id, info),
            ParkingOccupiedSpaces(coordinator, parking_id, info),
            ParkingOccupancyRate(coordinator, parking_id, info),
        ])
    health_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id, "api")},
        name="VDL Parkings API", manufacturer="Ville de Luxembourg",
        model="API diagnostics",
    )
    entities.extend([
        ApiLastSuccess(coordinator, health_info),
        ApiConsecutiveFailures(coordinator, health_info),
    ])
    async_add_entities(entities)


class ParkingSensor(CoordinatorEntity, SensorEntity):
    """Base class for parking sensors."""
    _attr_has_entity_name = True
    _attr_entity_registry_enabled_default = True

    def __init__(self, coordinator, parking_id, device_info):
        super().__init__(coordinator)
        self.parking_id = parking_id
        self._device_info = device_info

    @property
    def device_info(self):
        return self._device_info

    @property
    def extra_state_attributes(self):
        return {"last_updated": self.coordinator.data[self.parking_id].get("last_updated")}


class ParkingAvailableSpaces(ParkingSensor):
    _attr_translation_key = "available_spaces"
    _attr_state_class = SensorStateClass.MEASUREMENT
    @property
    def unique_id(self): return f"vdl_parking_{self.parking_id}_available_spaces"
    @property
    def native_value(self): return self.coordinator.data[self.parking_id]["available_spaces"]


class ParkingTotalCapacity(ParkingSensor):
    _attr_translation_key = "total_capacity"
    _attr_state_class = SensorStateClass.MEASUREMENT
    @property
    def unique_id(self): return f"vdl_parking_{self.parking_id}_total_capacity"
    @property
    def native_value(self): return self.coordinator.data[self.parking_id]["total_capacity"]


class ParkingOccupiedSpaces(ParkingSensor):
    _attr_translation_key = "occupied_spaces"
    _attr_state_class = SensorStateClass.MEASUREMENT
    @property
    def unique_id(self): return f"vdl_parking_{self.parking_id}_occupied_spaces"
    @property
    def native_value(self): return self.coordinator.data[self.parking_id]["occupied_spaces"]


class ParkingOccupancyRate(ParkingSensor):
    _attr_translation_key = "occupancy_rate"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"
    @property
    def unique_id(self): return f"vdl_parking_{self.parking_id}_occupancy_rate"
    @property
    def native_value(self): return self.coordinator.data[self.parking_id]["occupancy_rate"]


class ApiLastSuccess(CoordinatorEntity, SensorEntity):
    """Timestamp of the last successful API response."""
    _attr_name = "Last successful API response"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = "timestamp"
    _attr_has_entity_name = True
    def __init__(self, coordinator, device_info):
        super().__init__(coordinator)
        self._device_info = device_info
    @property
    def device_info(self): return self._device_info
    @property
    def unique_id(self): return "vdl_parkings_api_last_success"
    @property
    def native_value(self): return self.coordinator.last_success
    @property
    def extra_state_attributes(self):
        return {"last_attempt": self.coordinator.last_attempt,
                "last_error": self.coordinator.last_error}


class ApiConsecutiveFailures(CoordinatorEntity, SensorEntity):
    """Number of consecutive failed API requests."""
    _attr_name = "API consecutive failures"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    def __init__(self, coordinator, device_info):
        super().__init__(coordinator)
        self._device_info = device_info
    @property
    def device_info(self): return self._device_info
    @property
    def unique_id(self): return "vdl_parkings_api_consecutive_failures"
    @property
    def native_value(self): return self.coordinator.consecutive_failures
