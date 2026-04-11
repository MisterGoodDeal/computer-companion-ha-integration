from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import ComputerCompanionApiError
from .const import DOMAIN
from .coordinator import ComputerCompanionCoordinator
from .entity import CompanionEntity

_LOGGER = logging.getLogger(__name__)

PC_POWER_DESC = SwitchEntityDescription(
    key="host_pc",
    translation_key="host_pc",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ComputerCompanionCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    async_add_entities([HostPcSwitch(coordinator, PC_POWER_DESC)])


class HostPcSwitch(CompanionEntity, SwitchEntity):
    def __init__(
        self,
        coordinator: ComputerCompanionCoordinator,
        description: SwitchEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"

    @property
    def available(self) -> bool:
        return True

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.last_update_success:
            return False
        return bool(self.coordinator.data)

    async def async_turn_on(self) -> None:
        await self.coordinator.async_send_wake_on_lan()

    async def async_turn_off(self) -> None:
        try:
            await self.coordinator.api.post_power("shutdown")
        except ComputerCompanionApiError as err:
            _LOGGER.error("Shutdown failed: %s", err)
