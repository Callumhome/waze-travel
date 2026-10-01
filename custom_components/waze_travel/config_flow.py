"""Config flow for Waze Travel."""

from __future__ import annotations

import asyncio
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector

from .const import (
    CONF_AVOID_FERRIES,
    CONF_AVOID_SUBSCRIPTION_ROADS,
    CONF_AVOID_TOLL_ROADS,
    CONF_DESTINATION,
    CONF_DISTANCE_UNIT,
    CONF_ORIGIN,
    CONF_REALTIME,
    CONF_REGION,
    CONF_SCAN_INTERVAL,
    CONF_VEHICLE_TYPE,
    DEFAULT_AVOID_FERRIES,
    DEFAULT_AVOID_SUBSCRIPTION_ROADS,
    DEFAULT_AVOID_TOLL_ROADS,
    DEFAULT_DISTANCE_UNIT,
    DEFAULT_REALTIME,
    DEFAULT_REGION,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_VEHICLE_TYPE,
    DOMAIN,
    DISTANCE_UNITS,
    MIN_SCAN_INTERVAL,
    REGIONS,
    VEHICLE_TYPES,
)

_LOGGER = logging.getLogger(__name__)


def _schema(defaults: dict) -> vol.Schema:
    """Build the user form schema."""
    return vol.Schema(
        {
            vol.Required(
                CONF_NAME,
                default=defaults.get(CONF_NAME, "Waze Travel"),
            ): str,
            vol.Required(
                CONF_ORIGIN,
                default=defaults.get(CONF_ORIGIN, ""),
            ): str,
            vol.Required(
                CONF_DESTINATION,
                default=defaults.get(CONF_DESTINATION, ""),
            ): str,
            vol.Required(
                CONF_REGION,
                default=defaults.get(CONF_REGION, DEFAULT_REGION),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=REGIONS,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_REALTIME,
                default=defaults.get(
                    CONF_REALTIME, DEFAULT_REALTIME
                ),
            ): bool,
            vol.Required(
                CONF_VEHICLE_TYPE,
                default=defaults.get(
                    CONF_VEHICLE_TYPE, DEFAULT_VEHICLE_TYPE
                ),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=VEHICLE_TYPES,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_DISTANCE_UNIT,
                default=defaults.get(
                    CONF_DISTANCE_UNIT,
                    DEFAULT_DISTANCE_UNIT,
                ),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=DISTANCE_UNITS,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_AVOID_TOLL_ROADS,
                default=defaults.get(
                    CONF_AVOID_TOLL_ROADS,
                    DEFAULT_AVOID_TOLL_ROADS,
                ),
            ): bool,
            vol.Required(
                CONF_AVOID_SUBSCRIPTION_ROADS,
                default=defaults.get(
                    CONF_AVOID_SUBSCRIPTION_ROADS,
                    DEFAULT_AVOID_SUBSCRIPTION_ROADS,
                ),
            ): bool,
            vol.Required(
                CONF_AVOID_FERRIES,
                default=defaults.get(
                    CONF_AVOID_FERRIES,
                    DEFAULT_AVOID_FERRIES,
                ),
            ): bool,
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=defaults.get(
                    CONF_SCAN_INTERVAL,
                    DEFAULT_SCAN_INTERVAL,
                ),
            ): vol.All(
                vol.Coerce(int),
                vol.Range(min=MIN_SCAN_INTERVAL, max=3600),
            ),
        }
    )


def _resolve_location(hass: HomeAssistant, value: str) -> str:
    """Resolve a Home Assistant location entity to GPS coordinates."""
    value = value.strip()
    entity_id = value.lower()

    if not entity_id.startswith(
        ("person.", "zone.", "device_tracker.")
    ):
        return value

    state = hass.states.get(entity_id)

    if state is None:
        raise ValueError(
            f"Home Assistant entity was not found: {entity_id}"
        )

    latitude = state.attributes.get("latitude")
    longitude = state.attributes.get("longitude")

    if latitude is None or longitude is None:
        raise ValueError(
            f"Entity {entity_id} has no latitude/longitude. "
            "Check that its location is available in Home Assistant."
        )

    return f"{latitude},{longitude}"


async def _test_route(
    hass: HomeAssistant,
    data: dict,
) -> None:
    """Validate the route using Waze."""
    from pywaze import route_calculator

    origin = _resolve_location(hass, data[CONF_ORIGIN])
    destination = _resolve_location(hass, data[CONF_DESTINATION])

    region = data[CONF_REGION]
    vehicle_type = (
        None
        if data[CONF_VEHICLE_TYPE] == "car"
        else data[CONF_VEHICLE_TYPE]
    )

    avoid_toll_roads = data[CONF_AVOID_TOLL_ROADS]
    avoid_subscription_roads = data[
        CONF_AVOID_SUBSCRIPTION_ROADS
    ]
    avoid_ferries = data[CONF_AVOID_FERRIES]
    real_time = data[CONF_REALTIME]

    def calculate_route():
        """Run the Waze client in a separate event loop."""

        async def run():
            async with route_calculator.WazeRouteCalculator(
                region=region
            ) as client:
                return await client.calc_routes(
                    origin,
                    destination,
                    vehicle_type=vehicle_type,
                    avoid_toll_roads=avoid_toll_roads,
                    avoid_subscription_roads=(
                        avoid_subscription_roads
                    ),
                    avoid_ferries=avoid_ferries,
                    real_time=real_time,
                )

        return asyncio.run(run())

    routes = await hass.async_add_executor_job(calculate_route)

    if not routes:
        raise ValueError("Waze returned no routes")


class WazeTravelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Waze Travel config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup."""
        errors = {}

        if user_input is not None:
            user_input[CONF_ORIGIN] = user_input[
                CONF_ORIGIN
            ].strip()
            user_input[CONF_DESTINATION] = user_input[
                CONF_DESTINATION
            ].strip()

            await self.async_set_unique_id(
                f"{user_input[CONF_ORIGIN]}|"
                f"{user_input[CONF_DESTINATION]}|"
                f"{user_input[CONF_REGION]}".lower()
            )
            self._abort_if_unique_id_configured()

            try:
                await _test_route(self.hass, user_input)
            except Exception as err:
                _LOGGER.warning(
                    "Unable to validate Waze route: %s",
                    err,
                    exc_info=True,
                )
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(user_input or {}),
            errors=errors,
        )
