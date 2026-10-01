
"""Data coordinator for Waze Travel."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_AVOID_FERRIES,
    CONF_AVOID_SUBSCRIPTION_ROADS,
    CONF_AVOID_TOLL_ROADS,
    CONF_DESTINATION,
    CONF_ORIGIN,
    CONF_REALTIME,
    CONF_REGION,
    CONF_SCAN_INTERVAL,
    CONF_VEHICLE_TYPE,
    DEFAULT_TIMEOUT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def _resolve_location(hass: HomeAssistant, value: str) -> str:
    """Resolve a Home Assistant location entity to coordinates."""
    value = value.strip()

    if not value.startswith(
        ("person.", "zone.", "device_tracker.")
    ):
        return value

    state = hass.states.get(value)
    if state is None:
        raise ValueError(
            f"Home Assistant entity was not found: {value}"
        )

    latitude = state.attributes.get("latitude")
    longitude = state.attributes.get("longitude")

    if latitude is None or longitude is None:
        raise ValueError(
            f"Entity {value} has no latitude/longitude. "
            "Check that its location tracker is updating."
        )

    return f"{latitude},{longitude}"


class WazeTravelCoordinator(DataUpdateCoordinator):
    """Fetch route data from Waze."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.entry = entry

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=entry.data[CONF_SCAN_INTERVAL]
            ),
            always_update=False,
        )

    async def _async_update_data(self):
        """Update route information."""
        from pywaze import route_calculator

        data = self.entry.data

        try:
            origin = _resolve_location(
                self.hass, data[CONF_ORIGIN]
            )
            destination = _resolve_location(
                self.hass, data[CONF_DESTINATION]
            )

            async with route_calculator.WazeRouteCalculator(
                region=data[CONF_REGION],
                timeout=DEFAULT_TIMEOUT,
            ) as client:
                routes = await client.calc_routes(
                    origin,
                    destination,
                    vehicle_type=(
                        None
                        if data[CONF_VEHICLE_TYPE] == "car"
                        else data[CONF_VEHICLE_TYPE]
                    ),
                    avoid_toll_roads=data[
                        CONF_AVOID_TOLL_ROADS
                    ],
                    avoid_subscription_roads=data[
                        CONF_AVOID_SUBSCRIPTION_ROADS
                    ],
                    avoid_ferries=data[CONF_AVOID_FERRIES],
                    alternatives=3,
                    real_time=data[CONF_REALTIME],
                )

        except Exception as err:
            _LOGGER.warning(
                "Unable to retrieve Waze route: %s",
                err,
            )
            raise UpdateFailed(
                f"Unable to retrieve Waze route: {err}"
            ) from err

        if not routes:
            raise UpdateFailed("Waze returned no routes")

        best = routes[0]

        return {
            "duration": best.duration,
            "distance": best.distance,
            "name": best.name,
            "street_names": best.street_names,
            "routes": [
                {
                    "duration": route.duration,
                    "distance": route.distance,
                    "name": route.name,
                    "street_names": route.street_names,
                }
                for route in routes
            ],
        }
