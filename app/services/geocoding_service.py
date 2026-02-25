"""Geocoding service for location resolution."""

from typing import Optional

from app.core.config import settings
from app.core.exceptions import LocationResolutionException
from app.core.logging import get_logger
from app.integrations.external_api import ExternalAPIClient
from app.utils.cache import TTLCache

logger = get_logger(__name__)

# Global cache for geocoding results
geocoding_cache: TTLCache = TTLCache(max_size=500, default_ttl=86400)


class GeocodingService:
    """Service for geocoding locations to coordinates."""

    def __init__(self) -> None:
        self.api_key = settings.GEOCODING_API_KEY
        self.base_url = "https://nominatim.openstreetmap.org"

    async def resolve_location(self, location: str) -> tuple[float, float]:
        """Resolve location name to latitude and longitude.

        Uses OpenStreetMap Nominatim API (free, no key required).
        Falls back to alternative geocoding if needed.
        """
        cache_key = f"geocode:{location.lower()}"
        cached = await geocoding_cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for location: {location}")
            return cached

        try:
            async with ExternalAPIClient(
                name="Nominatim",
                base_url=self.base_url,
            ) as client:
                result = await client.get(
                    "/search",
                    params={
                        "q": location,
                        "format": "json",
                        "limit": 1,
                    },
                    headers={"User-Agent": "WeatherApp/1.0"},
                )

                if not result:
                    raise LocationResolutionException(location)

                first_result = result[0]
                latitude = float(first_result["lat"])
                longitude = float(first_result["lon"])

                # Cache the result
                await geocoding_cache.set(
                    cache_key,
                    (latitude, longitude),
                    ttl_seconds=86400,  # 24 hours
                )

                logger.info(
                    f"Resolved location '{location}' to "
                    f"({latitude}, {longitude})"
                )
                return latitude, longitude

        except LocationResolutionException:
            raise
        except Exception as e:
            logger.error(f"Failed to resolve location '{location}': {str(e)}")
            raise LocationResolutionException(location)
