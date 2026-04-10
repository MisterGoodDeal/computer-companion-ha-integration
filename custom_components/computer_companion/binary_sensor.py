from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ComputerCompanionCoordinator
from .entity import CompanionEntity

WINDOWS_DESC = BinarySensorEntityDescription(
    key="windows",
    translation_key="windows",
)

PRESENCE_DESC = BinarySensorEntityDescription(
    key="agent_presence",
    translation_key="agent_presence",
    device_class=BinarySensorDeviceClass.PRESENCE,
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
            WindowsBinarySensor(coordinator, WINDOWS_DESC),
            AgentPresenceBinarySensor(coordinator, PRESENCE_DESC),
        ]
    )


class WindowsBinarySensor(CompanionEntity, BinarySensorEntity):
    def __init__(
        self,
        coordinator: ComputerCompanionCoordinator,
        description: BinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        return bool(self.coordinator.data.get("windows"))


class AgentPresenceBinarySensor(CompanionEntity, BinarySensorEntity):
    def __init__(
        self,
        coordinator: ComputerCompanionCoordinator,
        description: BinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.last_update_success:
            return False
        return bool(self.coordinator.data)
