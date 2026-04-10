from __future__ import annotations

from typing import Final

DOMAIN: Final = "computer_companion"

CONF_TOKEN: Final = "token"

DEFAULT_PORT: Final = 8745

API_HEALTH_PATH: Final = "/health"
API_STATUS_PATH: Final = "/api/v1/status"
API_POWER_PATH: Final = "/api/v1/power"
API_APPS_PATH: Final = "/api/v1/apps"
API_LAUNCH_PATH: Final = "/api/v1/apps/launch"
API_NETWORK_MAC_PATH: Final = "/api/v1/network/mac"

POWER_ACTIONS: Final[tuple[str, ...]] = (
    "shutdown",
    "restart",
    "sleep",
    "hibernate",
    "abort",
)
