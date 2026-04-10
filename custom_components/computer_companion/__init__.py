from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ComputerCompanionApi, ComputerCompanionApiError, ComputerCompanionAuthError
from .const import CONF_TOKEN, DOMAIN, POWER_ACTIONS
from .coordinator import ComputerCompanionCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SELECT,
]

SERVICE_POWER = "power"
SERVICE_LAUNCH = "launch"

SERVICE_POWER_SCHEMA = vol.Schema(
    {
        vol.Required("config_entry"): str,
        vol.Required("action"): vol.In(POWER_ACTIONS),
    }
)

SERVICE_LAUNCH_SCHEMA = vol.Schema(
    {
        vol.Required("config_entry"): str,
        vol.Required("path"): str,
        vol.Optional("args", default=[]): [str],
    }
)


def _get_coordinator(hass: HomeAssistant, entry_id: str) -> ComputerCompanionCoordinator:
    entry_data = hass.data.get(DOMAIN, {}).get(entry_id)
    if not entry_data:
        raise ServiceValidationError("Unknown config entry")
    return entry_data["coordinator"]


async def _async_handle_power(hass: HomeAssistant, call: ServiceCall) -> None:
    entry_id = call.data["config_entry"]
    entry = hass.config_entries.async_get_entry(entry_id)
    if entry is None or entry.domain != DOMAIN:
        raise ServiceValidationError("Invalid config entry")
    coordinator = _get_coordinator(hass, entry_id)
    action = call.data["action"]
    try:
        await coordinator.api.post_power(action)
    except ComputerCompanionAuthError as err:
        raise HomeAssistantError("Authentication failed") from err
    except ComputerCompanionApiError as err:
        raise HomeAssistantError(str(err)) from err


async def _async_handle_launch(hass: HomeAssistant, call: ServiceCall) -> None:
    entry_id = call.data["config_entry"]
    entry = hass.config_entries.async_get_entry(entry_id)
    if entry is None or entry.domain != DOMAIN:
        raise ServiceValidationError("Invalid config entry")
    coordinator = _get_coordinator(hass, entry_id)
    path = call.data["path"]
    args = call.data.get("args") or []
    try:
        await coordinator.api.post_launch(path, args if args else None)
    except ComputerCompanionAuthError as err:
        raise HomeAssistantError("Authentication failed") from err
    except ComputerCompanionApiError as err:
        raise HomeAssistantError(str(err)) from err


def _ensure_services(hass: HomeAssistant) -> None:
    bucket = hass.data.setdefault(DOMAIN, {})
    if bucket.get("_services_registered"):
        return

    async def power_handler(call: ServiceCall) -> None:
        await _async_handle_power(hass, call)

    async def launch_handler(call: ServiceCall) -> None:
        await _async_handle_launch(hass, call)

    hass.services.async_register(
        DOMAIN,
        SERVICE_POWER,
        power_handler,
        schema=SERVICE_POWER_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_LAUNCH,
        launch_handler,
        schema=SERVICE_LAUNCH_SCHEMA,
    )
    bucket["_services_registered"] = True


def _remove_services_if_last(hass: HomeAssistant, entry_id: str) -> None:
    others = [
        e
        for e in hass.config_entries.async_entries(DOMAIN)
        if e.entry_id != entry_id
    ]
    if others:
        return
    if hass.services.has_service(DOMAIN, SERVICE_POWER):
        hass.services.async_remove(DOMAIN, SERVICE_POWER)
    if hass.services.has_service(DOMAIN, SERVICE_LAUNCH):
        hass.services.async_remove(DOMAIN, SERVICE_LAUNCH)
    hass.data.get(DOMAIN, {}).pop("_services_registered", None)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    api = ComputerCompanionApi(
        session,
        str(entry.data[CONF_HOST]).strip(),
        int(entry.data[CONF_PORT]),
        str(entry.data[CONF_TOKEN]),
    )
    coordinator = ComputerCompanionCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _ensure_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    _remove_services_if_last(hass, entry.entry_id)
