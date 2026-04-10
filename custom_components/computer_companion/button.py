from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import ComputerCompanionApiError
from .const import DOMAIN
from .coordinator import ComputerCompanionCoordinator
from .entity import WindowsOnlyEntity

_LOGGER = logging.getLogger(__name__)

REFRESH_DESC = ButtonEntityDescription(
    key="refresh_apps",
    translation_key="refresh_apps",
    entity_category=EntityCategory.CONFIG,
)

LAUNCH_DESC = ButtonEntityDescription(
    key="launch_selected",
    translation_key="launch_selected",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ComputerCompanionCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    async_add_entities(
        [
            RefreshAppsButton(coordinator, REFRESH_DESC),
            LaunchSelectedButton(coordinator, LAUNCH_DESC),
        ]
    )


class RefreshAppsButton(WindowsOnlyEntity, ButtonEntity):
    def __init__(
        self,
        coordinator: ComputerCompanionCoordinator,
        description: ButtonEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"

    async def async_press(self) -> None:
        try:
            await self.coordinator.async_refresh_apps()
        except ComputerCompanionApiError as err:
            _LOGGER.error("Failed to refresh app list: %s", err)


class LaunchSelectedButton(WindowsOnlyEntity, ButtonEntity):
    def __init__(
        self,
        coordinator: ComputerCompanionCoordinator,
        description: ButtonEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"

    async def async_press(self) -> None:
        eid = self.coordinator.manual_launch_text_entity_id
        if eid:
            state = self.hass.states.get(eid)
            if state and state.state not in ("unknown", "unavailable", ""):
                custom = state.state.strip()
                if custom:
                    try:
                        await self.coordinator.api.post_launch(custom)
                    except ComputerCompanionApiError as err:
                        _LOGGER.error("Launch failed: %s", err)
                    return

        label = self.coordinator.selected_launch_label
        if not label:
            _LOGGER.warning(
                "No custom path set and no application selected in the list"
            )
            return
        path = self.coordinator.app_options.get(label)
        if not path:
            return
        try:
            await self.coordinator.api.post_launch(path)
        except ComputerCompanionApiError as err:
            _LOGGER.error("Launch failed: %s", err)
