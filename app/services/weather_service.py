"""Weather data service."""

from datetime import datetime
from typing import Any, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.external_api import ExternalAPIClient
from app.utils.cache import TTLCache

logger = get_logger(__name__)

# Global cache for weather data
weather_cache: TTLCache = TTLCache(max_size=1000, default_ttl=3600)


class WeatherService:
    """Service for fetching weather data."""

    def __init__(self) -> None:
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org"

    async def get_weather(
        self,
        latitude: float,
        longitude: float,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[str, Any]:
        """Get weather data for location and date range.

        Uses OpenWeather API.
        """
        cache_key = (
            f"weather:{latitude}:{longitude}:"
            f"{start_date.date()}:{end_date.date()}"
        )
        cached = await weather_cache.get(cache_key)
        if cached:
            logger.info(
                f"Cache hit for weather: ({latitude}, {longitude})"
            )
            return cached

        try:
            async with ExternalAPIClient(
                name="OpenWeather",
                base_url=self.base_url,
            ) as client:
                # OpenWeather Current Weather API
                result = await client.get(
                    "/data/2.5/weather",
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "appid": self.api_key,
                        "units": "metric",
                    },
                )

                weather_data = {
                    "temperature": result.get("main", {}).get("temp"),
                    "feels_like": result.get("main", {}).get("feels_like"),
                    "humidity": result.get("main", {}).get("humidity"),
                    "pressure": result.get("main", {}).get("pressure"),
                    "wind_speed": result.get("wind", {}).get("speed"),
                    "wind_direction": result.get("wind", {}).get("deg"),
                    "clouds": result.get("clouds", {}).get("all"),
                    "description": result.get("weather", [{}])[0].get("description"),
                    "main_weather": result.get("weather", [{}])[0].get("main"),
                    "visibility": result.get("visibility"),
                    "rain_1h": result.get("rain", {}).get("1h"),
                    "snow_1h": result.get("snow", {}).get("1h"),
                    "sunrise": result.get("sys", {}).get("sunrise"),
                    "sunset": result.get("sys", {}).get("sunset"),
                }

                # Cache the result
                await weather_cache.set(
                    cache_key,
                    weather_data,
                    ttl_seconds=3600,
                )

                logger.info(
                    f"Fetched weather data for ({latitude}, {longitude})"
                )
                return weather_data

        except Exception as e:
            logger.error(f"Failed to fetch weather data: {str(e)}")
            raise

    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
    ) -> dict[str, Any]:
        """Get weather forecast for location."""
        cache_key = f"forecast:{latitude}:{longitude}"
        cached = await weather_cache.get(cache_key)
        if cached:
            return cached

        try:
            async with ExternalAPIClient(
                name="OpenWeather",
                base_url=self.base_url,
            ) as client:
                result = await client.get(
                    "/data/2.5/forecast",
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "appid": self.api_key,
                        "units": "metric",
                    },
                )

                forecast_data = {
                    "count": result.get("cnt"),
                    "list": result.get("list", [])[:8],  # Next 24 hours
                }

                await weather_cache.set(
                    cache_key,
                    forecast_data,
                    ttl_seconds=3600,
                )

                return forecast_data

        except Exception as e:
            logger.error(f"Failed to fetch forecast: {str(e)}")
            raise
