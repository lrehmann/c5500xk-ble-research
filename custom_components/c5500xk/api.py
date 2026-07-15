"""HTTP client for the C5500XK direct-Bluetooth collector."""

from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession


class CollectorApiError(Exception):
    """Collector request failed."""


class CollectorApi:
    def __init__(self, session: ClientSession, host: str, port: int, token: str) -> None:
        self._session = session
        self._base_url = f"http://{host}:{port}/v1"
        self._headers = {"Authorization": f"Bearer {token}"}

    async def async_status(self) -> dict[str, Any]:
        return await self._request("GET", "/status")

    async def async_action(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        return await self._request(
            "POST", f"/actions/{action}", json=parameters, request_timeout=90
        )

    async def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        request_timeout = kwargs.pop("request_timeout", 15)
        try:
            async with asyncio.timeout(request_timeout):
                async with self._session.request(
                    method,
                    self._base_url + path,
                    headers=self._headers,
                    **kwargs,
                ) as response:
                    payload = await response.json(content_type=None)
                    if response.status >= 400:
                        raise CollectorApiError(
                            payload.get("error", f"Collector returned HTTP {response.status}")
                        )
                    return payload
        except CollectorApiError:
            raise
        except (TimeoutError, ClientError, ClientResponseError, ValueError) as err:
            raise CollectorApiError(f"Unable to contact Bluetooth collector: {err}") from err
