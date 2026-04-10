from __future__ import annotations

from homeassistant.components.text import TextEntity, TextEntityDescription, TextMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ComputerCompanionCoordinator
from .entity import WindowsOnlyEntity

MANUAL_PATH_DESC = TextEntityDescription(
    key="manual_launch_path",
    translation_key="manual_launch_path",
    mode=TextMode.TEXT,
    native_min=0,
    native_max=2048,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ComputerCompanionCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    async_add_entities([ManualLaunchPathText(coordinator, MANUAL_PATH_DESC)])


class ManualLaunchPathText(WindowsOnlyEntity, TextEntity):
    def __init__(
        self,
        coordinator: ComputerCompanionCoordinator,
        description: TextEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"
        self._attr_native_value = ""

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.coordinator.manual_launch_text_entity_id = self.entity_id

    async def async_will_remove_from_hass(self) -> None:
        self.coordinator.manual_launch_text_entity_id = None
        await super().async_will_remove_from_hass()

    async def async_set_value(self, value: str) -> None:
        self._attr_native_value = value
        self.async_write_ha_state()
