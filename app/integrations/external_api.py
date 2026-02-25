"""External API integration base."""

from typing import Any, Optional

import httpx

from app.core.config import settings
from app.core.exceptions import ExternalAPIException
from app.core.logging import get_logger
from app.utils.retry import RetryConfig, retry_with_backoff

logger = get_logger(__name__)


class ExternalAPIClient:
    """Base client for external API calls."""

    def __init__(
        self,
        name: str,
        base_url: str,
        timeout: Optional[int] = None,
        retry_config: Optional[RetryConfig] = None,
    ) -> None:
        self.name = name
        self.base_url = base_url
        self.timeout = timeout or settings.API_TIMEOUT
        self.retry_config = retry_config or RetryConfig(
            max_attempts=settings.API_RETRY_ATTEMPTS,
            initial_delay=settings.API_RETRY_DELAY,
        )
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "ExternalAPIClient":
        """Async context manager entry."""
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    async def get(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make GET request with retry."""
        if not self.client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        async def _request() -> dict[str, Any]:
            try:
                response = await self.client.get(
                    endpoint,
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"{self.name} API error: {e.status_code} - {e.response.text}"
                )
                raise
            except httpx.RequestError as e:
                logger.error(f"{self.name} request error: {str(e)}")
                raise

        try:
            return await retry_with_backoff(_request, config=self.retry_config)
        except Exception as e:
            raise ExternalAPIException(
                service_name=self.name,
                message=f"Failed to fetch from {endpoint}",
                original_error=str(e),
            )

    async def post(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make POST request with retry."""
        if not self.client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        async def _request() -> dict[str, Any]:
            try:
                response = await self.client.post(
                    endpoint,
                    data=data,
                    json=json,
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"{self.name} API error: {e.status_code} - {e.response.text}"
                )
                raise
            except httpx.RequestError as e:
                logger.error(f"{self.name} request error: {str(e)}")
                raise

        try:
            return await retry_with_backoff(_request, config=self.retry_config)
        except Exception as e:
            raise ExternalAPIException(
                service_name=self.name,
                message=f"Failed to post to {endpoint}",
                original_error=str(e),
            )
