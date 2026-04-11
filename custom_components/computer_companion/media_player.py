from __future__ import annotations

import logging

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.components.media_player.const import MediaPlayerState
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import ComputerCompanionApiError
from .const import DOMAIN
from .coordinator import ComputerCompanionCoordinator
from .entity import WindowsOnlyEntity

_LOGGER = logging.getLogger(__name__)

MEDIA_DESC_KEY = "windows_media"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ComputerCompanionCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    async_add_entities([WindowsMediaPlayer(coordinator)])


class WindowsMediaPlayer(WindowsOnlyEntity, MediaPlayerEntity):
    _attr_has_entity_name = True
    _attr_translation_key = MEDIA_DESC_KEY
    _attr_supported_features = (
        MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
    )

    def __init__(self, coordinator: ComputerCompanionCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{MEDIA_DESC_KEY}"

    async def _send_action(self, action: str) -> None:
        try:
            await self.coordinator.api.post_media_action(action)
        except ComputerCompanionApiError as err:
            _LOGGER.error("Media action %s failed: %s", action, err)

    @property
    def state(self) -> MediaPlayerState:
        return MediaPlayerState.IDLE

    async def async_media_play(self) -> None:
        await self._send_action("play_pause")

    async def async_media_pause(self) -> None:
        await self._send_action("play_pause")

    async def async_media_play_pause(self) -> None:
        await self._send_action("play_pause")

    async def async_media_stop(self) -> None:
        await self._send_action("stop")

    async def async_media_next_track(self) -> None:
        await self._send_action("next")

    async def async_media_previous_track(self) -> None:
        await self._send_action("previous")

    async def async_volume_up(self) -> None:
        await self._send_action("volume_up")

    async def async_volume_down(self) -> None:
        await self._send_action("volume_down")

    async def async_mute_volume(self, mute: bool) -> None:
        await self._send_action("mute")
