"""Air Quality Index (AQI) service."""

from typing import Any, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.external_api import ExternalAPIClient
from app.utils.cache import TTLCache

logger = get_logger(__name__)

# Global cache for AQI data
aqi_cache: TTLCache = TTLCache(max_size=500, default_ttl=3600)


class AQIService:
    """Service for fetching Air Quality Index data."""

    def __init__(self) -> None:
        self.api_key = settings.AQI_API_KEY
        self.base_url = "https://api.openweathermap.org"

    async def get_aqi(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[int]:
        """Get Air Quality Index for location.

        Returns AQI level (0-5, where 0 is best and 5 is worst).
        """
        cache_key = f"aqi:{latitude}:{longitude}"
        cached = await aqi_cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for AQI: ({latitude}, {longitude})")
            return cached

        try:
            async with ExternalAPIClient(
                name="OpenWeather",
                base_url=self.base_url,
            ) as client:
                result = await client.get(
                    "/data/2.5/air_quality",
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "appid": self.api_key,
                    },
                )

                aqi_value = result.get("list", [{}])[0].get("main", {}).get("aqi")

                if aqi_value is not None:
                    await aqi_cache.set(
                        cache_key,
                        aqi_value,
                        ttl_seconds=3600,
                    )

                    logger.info(
                        f"Fetched AQI data for ({latitude}, {longitude}): {aqi_value}"
                    )

                return aqi_value

        except Exception as e:
            logger.warning(f"Failed to fetch AQI data: {str(e)}")
            return None

    @staticmethod
    def get_aqi_description(aqi: int) -> str:
        """Get human-readable AQI description."""
        descriptions = {
            0: "Good",
            1: "Fair",
            2: "Moderate",
            3: "Poor",
            4: "Very Poor",
            5: "Extremely Poor",
        }
        return descriptions.get(aqi, "Unknown")

    @staticmethod
    def get_aqi_color(aqi: int) -> str:
        """Get color code for AQI level."""
        colors = {
            0: "green",
            1: "yellow",
            2: "orange",
            3: "red",
            4: "purple",
            5: "maroon",
        }
        return colors.get(aqi, "gray")
