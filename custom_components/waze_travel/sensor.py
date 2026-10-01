"""Sensors for Waze Travel."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DISTANCE_UNIT,
    DEFAULT_DISTANCE_UNIT,
    DOMAIN,
)
from .coordinator import WazeTravelCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
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

    def __init__(
        self,
        coordinator: WazeTravelCoordinator,
        entry: ConfigEntry,
    ) -> None:
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
        """Return route details as sensor attributes."""
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

    def __init__(
        self,
        coordinator: WazeTravelCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_duration"
        self._attr_name = "Travel time"

    @property
    def native_value(self):
        """Return travel duration in minutes."""
        if not self.coordinator.data:
            return None

        return round(self.coordinator.data["duration"], 1)


class WazeTravelDistanceSensor(WazeTravelSensorBase):
    """Travel distance sensor."""

    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_icon = "mdi:map-marker-distance"

    def __init__(
        self,
        coordinator: WazeTravelCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_distance"
        self._attr_name = "Distance"

    @property
    def _distance_unit(self) -> str:
        """Return the selected unit."""
        return self.entry.options.get(
            CONF_DISTANCE_UNIT,
            self.entry.data.get(
                CONF_DISTANCE_UNIT,
                DEFAULT_DISTANCE_UNIT,
            ),
        )

    @property
    def native_unit_of_measurement(self):
        """Return the selected distance unit."""
        if self._distance_unit == "km":
            return UnitOfLength.KILOMETERS
        return UnitOfLength.MILES

    @property
    def native_value(self):
        """Return distance in the selected unit."""
        if not self.coordinator.data:
            return None

        distance_km = float(self.coordinator.data["distance"])

        if self._distance_unit == "km":
            return round(distance_km, 2)

        return round(distance_km * 0.621371, 2)

    async def async_added_to_hass(self) -> None:
        """Register option changes and refresh the sensor."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.entry.add_update_listener(self._options_updated)
        )

    async def _options_updated(self, hass, entry) -> None:
        """Refresh the sensor after its options change."""
        self.async_write_ha_state()
