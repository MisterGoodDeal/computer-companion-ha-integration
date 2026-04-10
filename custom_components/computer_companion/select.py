from __future__ import annotations

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ComputerCompanionCoordinator
from .entity import WindowsOnlyEntity

PLATFORM_DESC = SelectEntityDescription(
    key="app_launch",
    translation_key="app_launch",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ComputerCompanionCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    async_add_entities([AppLaunchSelect(coordinator, PLATFORM_DESC)])


class AppLaunchSelect(WindowsOnlyEntity, SelectEntity):
    def __init__(
        self,
        coordinator: ComputerCompanionCoordinator,
        description: SelectEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"
        self._attr_current_option = None

    @property
    def options(self) -> list[str]:
        return list(self.coordinator.app_options.keys())

    @property
    def current_option(self) -> str | None:
        return self._attr_current_option

    async def async_select_option(self, option: str) -> None:
        if option not in self.coordinator.app_options:
            raise ValueError(f"Invalid option: {option}")
        self._attr_current_option = option
        self.coordinator.selected_launch_label = option
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        super()._handle_coordinator_update()
        cur = self._attr_current_option
        if cur and cur not in self.coordinator.app_options:
            self._attr_current_option = None
            self.coordinator.selected_launch_label = None
            self.async_write_ha_state()
