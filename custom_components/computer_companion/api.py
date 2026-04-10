from __future__ import annotations

import asyncio
from typing import Any

import aiohttp
from yarl import URL

from .const import (
    API_APPS_PATH,
    API_HEALTH_PATH,
    API_LAUNCH_PATH,
    API_NETWORK_MAC_PATH,
    API_POWER_PATH,
    API_STATUS_PATH,
)

TIMEOUT_DEFAULT = aiohttp.ClientTimeout(total=30, connect=10)
TIMEOUT_APPS_SCAN = aiohttp.ClientTimeout(total=300, connect=10)


class ComputerCompanionApiError(Exception):
    pass


class ComputerCompanionAuthError(ComputerCompanionApiError):
    pass


class ComputerCompanionApi:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int,
        token: str,
    ) -> None:
        self._session = session
        self._base = URL.build(scheme="http", host=host, port=port)
        self._auth = {"Authorization": f"Bearer {token.strip()}"}

    async def get_health(self) -> dict[str, Any]:
        url = self._base.join(URL(API_HEALTH_PATH))
        try:
            async with self._session.get(url, timeout=TIMEOUT_DEFAULT) as resp:
                if resp.status != 200:
                    raise ComputerCompanionApiError(f"HTTP {resp.status}")
                data = await resp.json()
                if not data.get("ok") or data.get("service") != "computer-companion":
                    raise ComputerCompanionApiError("invalid_health_payload")
                return data
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise ComputerCompanionApiError(str(err)) from err

    async def get_status(self) -> dict[str, Any]:
        url = self._base.join(URL(API_STATUS_PATH))
        try:
            async with self._session.get(
                url, headers=self._auth, timeout=TIMEOUT_DEFAULT
            ) as resp:
                if resp.status == 401:
                    raise ComputerCompanionAuthError()
                if resp.status != 200:
                    text = await resp.text()
                    raise ComputerCompanionApiError(f"HTTP {resp.status}: {text[:200]}")
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise ComputerCompanionApiError(str(err)) from err

    async def get_network_mac(self) -> dict[str, Any]:
        url = self._base.join(URL(API_NETWORK_MAC_PATH))
        try:
            async with self._session.get(
                url, headers=self._auth, timeout=TIMEOUT_DEFAULT
            ) as resp:
                if resp.status == 401:
                    raise ComputerCompanionAuthError()
                if resp.status != 200:
                    text = await resp.text()
                    raise ComputerCompanionApiError(f"HTTP {resp.status}: {text[:200]}")
                return await resp.json()
        except ComputerCompanionAuthError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise ComputerCompanionApiError(str(err)) from err

    async def post_power(self, action: str) -> dict[str, Any]:
        url = self._base.join(URL(API_POWER_PATH))
        try:
            async with self._session.post(
                url,
                headers={**self._auth, "Content-Type": "application/json"},
                json={"action": action},
                timeout=TIMEOUT_DEFAULT,
            ) as resp:
                if resp.status == 401:
                    raise ComputerCompanionAuthError()
                data = await resp.json()
                if resp.status != 200:
                    err = data.get("error", resp.status)
                    raise ComputerCompanionApiError(str(err))
                return data
        except ComputerCompanionAuthError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise ComputerCompanionApiError(str(err)) from err

    async def get_apps(self, only_with_install_location: bool = True) -> dict[str, Any]:
        url = self._base.join(URL(API_APPS_PATH))
        q = "1" if only_with_install_location else "0"
        try:
            async with self._session.get(
                url,
                headers=self._auth,
                params={"onlyWithInstallLocation": q},
                timeout=TIMEOUT_APPS_SCAN,
            ) as resp:
                if resp.status == 401:
                    raise ComputerCompanionAuthError()
                if resp.status != 200:
                    text = await resp.text()
                    raise ComputerCompanionApiError(f"HTTP {resp.status}: {text[:200]}")
                return await resp.json()
        except ComputerCompanionAuthError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise ComputerCompanionApiError(str(err)) from err

    async def post_launch(self, path: str, args: list[str] | None = None) -> dict[str, Any]:
        url = self._base.join(URL(API_LAUNCH_PATH))
        body: dict[str, Any] = {"path": path}
        if args:
            body["args"] = args
        try:
            async with self._session.post(
                url,
                headers={**self._auth, "Content-Type": "application/json"},
                json=body,
                timeout=TIMEOUT_DEFAULT,
            ) as resp:
                if resp.status == 401:
                    raise ComputerCompanionAuthError()
                data = await resp.json()
                if resp.status != 200:
                    err = data.get("error", resp.status)
                    raise ComputerCompanionApiError(str(err))
                return data
        except ComputerCompanionAuthError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise ComputerCompanionApiError(str(err)) from err
