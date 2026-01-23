"""AC Infinity API client."""

import logging
from typing import Any
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

API_BASE = "http://www.acinfinityserver.com"
LOGIN_ENDPOINT = f"{API_BASE}/api/user/appUserLogin"
DEVICES_ENDPOINT = f"{API_BASE}/api/user/devInfoListAll"
GET_SETTINGS_ENDPOINT = f"{API_BASE}/api/dev/getdevModeSettingList"
SET_MODE_ENDPOINT = f"{API_BASE}/api/dev/addDevMode"


class ACInfinityClient:
    """Client for AC Infinity cloud API with read/write support."""

    def __init__(self, email: str, password: str) -> None:
        self.email = email
        self.password = password
        self.token: str | None = None
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
        })

    def authenticate(self) -> bool:
        """Authenticate with AC Infinity API and get token."""
        try:
            # Note: API has typo - appPasswordl with 'l'
            # Password truncated to 25 chars per API limitation
            response = self.session.post(
                LOGIN_ENDPOINT,
                data={
                    "appEmail": self.email,
                    "appPasswordl": self.password[:25],
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("code") != 200:
                logger.error("Authentication failed: %s", data.get("msg", "Unknown error"))
                return False

            self.token = data.get("data", {}).get("appId")
            if not self.token:
                logger.error("No appId in authentication response")
                return False

            logger.info("Successfully authenticated with AC Infinity API")
            return True

        except requests.RequestException as e:
            logger.error("Authentication request failed: %s", e)
            return False

    def get_devices(self) -> list[dict[str, Any]]:
        """Fetch all devices from AC Infinity API."""
        if not self.token:
            if not self.authenticate():
                return []

        try:
            response = self.session.post(
                DEVICES_ENDPOINT,
                data={"userId": self.token},
                headers={"token": self.token},
                timeout=30,
            )

            if response.status_code == 401:
                logger.warning("Token expired, re-authenticating")
                if not self.authenticate():
                    return []
                return self.get_devices()

            response.raise_for_status()
            data = response.json()

            if data.get("code") != 200:
                logger.error("Failed to get devices: %s", data.get("msg", "Unknown error"))
                return []

            return data.get("data", [])

        except requests.RequestException as e:
            logger.error("Failed to fetch devices: %s", e)
            return []

    def get_device_settings(self, controller_id: str, port: int) -> dict[str, Any] | None:
        """Get current settings for a device port."""
        if not self.token:
            if not self.authenticate():
                return None

        try:
            response = self.session.post(
                GET_SETTINGS_ENDPOINT,
                data={"devId": controller_id, "port": port},
                headers={"token": self.token},
                timeout=30,
            )

            if response.status_code == 401:
                logger.warning("Token expired, re-authenticating")
                if not self.authenticate():
                    return None
                return self.get_device_settings(controller_id, port)

            response.raise_for_status()
            data = response.json()

            if data.get("code") != 200:
                logger.error("Failed to get settings: %s", data.get("msg"))
                return None

            return data.get("data", {})

        except requests.RequestException as e:
            logger.error("Failed to get device settings: %s", e)
            return None

    def set_device_speed(self, controller_id: str, port: int, speed: int) -> bool:
        """Set the speed of a device.

        This sets the device to ON mode with the specified speed.
        Speed is 0-10 for Cloudline fans.
        """
        if not self.token:
            if not self.authenticate():
                return False

        # Get current settings first
        settings = self.get_device_settings(controller_id, port)
        if not settings:
            logger.error("Cannot set speed: failed to get current settings")
            return False

        logger.info("Current settings for port %d: atType=%s, onSpead=%s, speak=%s",
                    port, settings.get("atType"), settings.get("onSpead"), settings.get("speak"))

        # Copy ALL settings from existing, then override what we need
        # This matches how the HA integration does it
        payload = {}
        for key, value in settings.items():
            # Skip nested objects/dicts
            if isinstance(value, dict):
                continue
            payload[key] = value

        # Override the speed-related fields
        # atType: 2 = ON mode (manual speed)
        # onSpead: speed when in ON mode (0-10)
        payload["devId"] = controller_id
        payload["port"] = port
        payload["atType"] = 2  # ON mode for manual speed control
        payload["onSpead"] = speed  # Target speed (note the typo in API)

        logger.debug("Sending payload: %s", payload)

        try:
            # API expects query string parameters
            url = f"{SET_MODE_ENDPOINT}?{urlencode(payload)}"
            response = self.session.post(
                url,
                headers={"token": self.token},
                timeout=30,
            )

            if response.status_code == 401:
                logger.warning("Token expired during set, re-authenticating")
                if not self.authenticate():
                    return False
                return self.set_device_speed(controller_id, port, speed)

            response.raise_for_status()
            data = response.json()

            logger.info("API response: %s", data)

            if data.get("code") != 200:
                logger.error("Failed to set speed: %s", data.get("msg"))
                return False

            logger.info("Successfully set controller %s port %d speed to %d", controller_id, port, speed)
            return True

        except requests.RequestException as e:
            logger.error("Failed to set device speed: %s", e)
            return False
