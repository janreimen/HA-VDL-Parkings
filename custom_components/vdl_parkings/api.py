"""VDL API client."""

import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)
API_URL = "https://www.vdl.lu/fr/parking/data.json"


class VdlParkingApi:
    """Small API client; Home Assistant owns the shared HTTP session."""

    def __init__(self, session):
        self._session = session

    async def fetch(self):
        """Fetch and validate the VDL parking payload."""
        async with self._session.get(API_URL, timeout=aiohttp.ClientTimeout(total=20)) as response:
            content_type = response.headers.get("Content-Type", "")
            response.raise_for_status()
            if "json" not in content_type.lower():
                preview = (await response.text())[:200]
                raise ValueError(
                    f"Unexpected VDL content type {content_type!r}; response: {preview}"
                )
            payload = await response.json(content_type=None)
            if not isinstance(payload, dict) or not isinstance(payload.get("parking"), list):
                raise ValueError("VDL response does not contain a parking list")
            return payload
