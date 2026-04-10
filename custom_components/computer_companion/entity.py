from __future__ import annotations

from typing import Any

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ComputerCompanionCoordinator


class CompanionEntity(CoordinatorEntity[ComputerCompanionCoordinator]):
    _attr_has_entity_name = True

    @property
    def device_info(self) -> dict[str, Any]:
        info: dict[str, Any] = {
            "identifiers": {(DOMAIN, self.coordinator.entry.entry_id)},
            "name": self.coordinator.entry.title,
            "manufacturer": "Computer Companion",
        }
        if self.coordinator.data and self.coordinator.data.get("platform"):
            info["model"] = self.coordinator.data["platform"]
        return info


class WindowsOnlyEntity(CompanionEntity):
    @property
    def available(self) -> bool:
        if not super().available:
            return False
        data = self.coordinator.data
        return bool(data and data.get("windows"))
