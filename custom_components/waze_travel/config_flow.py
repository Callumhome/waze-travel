"""Config flow for Waze Travel."""

from __future__ import annotations

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
    CONF_ORIGIN,
    CONF_REALTIME,
    CONF_REGION,
    CONF_SCAN_INTERVAL,
    CONF_VEHICLE_TYPE,
    DEFAULT_AVOID_FERRIES,
    DEFAULT_AVOID_SUBSCRIPTION_ROADS,
    DEFAULT_AVOID_TOLL_ROADS,
    DEFAULT_REALTIME,
    DEFAULT_REGION,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_VEHICLE_TYPE,
    DOMAIN,
    MIN_SCAN_INTERVAL,
    REGIONS,
    VEHICLE_TYPES,
)


def _schema(defaults: dict) -> vol.Schema:
    """Build the user form schema."""
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "Waze Travel")): str,
            vol.Required(CONF_ORIGIN, default=defaults.get(CONF_ORIGIN, "")): str,
            vol.Required(CONF_DESTINATION, default=defaults.get(CONF_DESTINATION, "")): str,
            vol.Required(
                CONF_REGION, default=defaults.get(CONF_REGION, DEFAULT_REGION)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=REGIONS,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_REALTIME, default=defaults.get(CONF_REALTIME, DEFAULT_REALTIME)
            ): bool,
            vol.Required(
                CONF_VEHICLE_TYPE,
                default=defaults.get(CONF_VEHICLE_TYPE, DEFAULT_VEHICLE_TYPE),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=VEHICLE_TYPES,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_AVOID_TOLL_ROADS,
                default=defaults.get(CONF_AVOID_TOLL_ROADS, DEFAULT_AVOID_TOLL_ROADS),
            ): bool,
            vol.Required(
                CONF_AVOID_SUBSCRIPTION_ROADS,
                default=defaults.get(
                    CONF_AVOID_SUBSCRIPTION_ROADS, DEFAULT_AVOID_SUBSCRIPTION_ROADS
                ),
            ): bool,
            vol.Required(
                CONF_AVOID_FERRIES,
                default=defaults.get(CONF_AVOID_FERRIES, DEFAULT_AVOID_FERRIES),
            ): bool,
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=defaults.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=3600)),
        }
    )


async def _test_route(hass: HomeAssistant, data: dict) -> None:
    """Validate the route by asking Waze for one calculation."""
    from pywaze import route_calculator

    async with route_calculator.WazeRouteCalculator(region=data[CONF_REGION]) as client:
        routes = await client.calc_routes(
            data[CONF_ORIGIN],
            data[CONF_DESTINATION],
            vehicle_type=None if data[CONF_VEHICLE_TYPE] == "car" else data[CONF_VEHICLE_TYPE],
            avoid_toll_roads=data[CONF_AVOID_TOLL_ROADS],
            avoid_subscription_roads=data[CONF_AVOID_SUBSCRIPTION_ROADS],
            avoid_ferries=data[CONF_AVOID_FERRIES],
            real_time=data[CONF_REALTIME],
        )
        if not routes:
            raise ValueError("No routes returned by Waze")


class WazeTravelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Waze Travel config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup."""
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_ORIGIN]}|{user_input[CONF_DESTINATION]}|{user_input[CONF_REGION]}".lower()
            )
            self._abort_if_unique_id_configured()
            try:
                await _test_route(self.hass, user_input)
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=_schema(user_input or {}), errors=errors
        )
