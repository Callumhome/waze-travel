"""Sensors for Waze Travel."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WazeTravelCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Waze Travel sensors."""
    coordinator: WazeTravelCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            WazeTravelDurationSensor(coordinator, entry),
            WazeTravelDistanceSensor(coordinator, entry),
        ]
    )


class WazeTravelSensorBase(CoordinatorEntity, SensorEntity):
    """Base sensor."""

    def __init__(self, coordinator: WazeTravelCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Waze Travel",
            model="Waze route",
        )

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return None
        return {
            "origin": self.entry.data["origin"],
            "destination": self.entry.data["destination"],
            "route": data.get("name"),
            "traffic_aware": self.entry.data["realtime"],
            "street_names": data.get("street_names", []),
            "alternatives": data.get("routes", []),
        }


class WazeTravelDurationSensor(WazeTravelSensorBase):
    """Travel duration sensor."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_icon = "mdi:car-clock"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_duration"
        self._attr_name = "Travel time"

    @property
    def native_value(self):
        return round(self.coordinator.data["duration"], 1) if self.coordinator.data else None


class WazeTravelDistanceSensor(WazeTravelSensorBase):
    """Travel distance sensor."""

    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_icon = "mdi:map-marker-distance"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_distance"
        self._attr_name = "Distance"

    @property
    def native_value(self):
        return round(self.coordinator.data["distance"], 2) if self.coordinator.data else None
