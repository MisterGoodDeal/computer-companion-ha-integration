from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ComputerCompanionApi, ComputerCompanionApiError, ComputerCompanionAuthError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=60)


class ComputerCompanionCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: ComputerCompanionApi,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.api = api
        self.entry = entry
        self.app_options: dict[str, str] = {}
        self.selected_launch_label: str | None = None
        self.manual_launch_text_entity_id: str | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.get_status()
        except ComputerCompanionAuthError as err:
            raise UpdateFailed("Authentication failed") from err
        except ComputerCompanionApiError as err:
            raise UpdateFailed(str(err)) from err

    async def async_refresh_apps(self) -> None:
        data = await self.api.get_apps()
        apps = data.get("apps", [])
        new_options: dict[str, str] = {}
        for row in apps:
            path = row.get("installLocation")
            if not path:
                continue
            name = str(row.get("name") or path)
            label = name
            base = name
            n = 1
            while label in new_options:
                label = f"{base} ({n})"
                n += 1
            new_options[label] = path
        self.app_options = new_options
        if (
            self.selected_launch_label
            and self.selected_launch_label not in self.app_options
        ):
            self.selected_launch_label = None
        self.async_update_listeners()
