"""Main weather application service orchestrating all business logic."""

import asyncio
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFoundException
from app.core.logging import get_logger
from app.models.weather import WeatherRequest
from app.repositories.weather_repository import WeatherRepository
from app.schemas.weather import WeatherRequestCreate, WeatherResponse, WeatherUpdateRequest
from app.services.aqi_service import AQIService
from app.services.geocoding_service import GeocodingService
from app.services.weather_service import WeatherService
from app.services.youtube_service import YouTubeService

logger = get_logger(__name__)


class WeatherApplicationService:
    """Main application service for weather operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = WeatherRepository(session)
        self.geocoding_service = GeocodingService()
        self.weather_service = WeatherService()
        self.aqi_service = AQIService()
        self.youtube_service = YouTubeService()

    async def create_weather_request(
        self,
        request: WeatherRequestCreate,
    ) -> WeatherResponse:
        """Create a new weather request with enriched data.

        Orchestrates:
        1. Geocoding - resolve location to coordinates
        2. Weather - fetch weather data
        3. AQI - fetch air quality index
        4. YouTube - fetch travel videos
        5. Store in database
        """
        logger.info(f"Creating weather request for {request.location}")

        # Resolve location to coordinates
        latitude, longitude = await self.geocoding_service.resolve_location(
            request.location
        )

        # Fetch data in parallel
        weather_data, aqi, videos = await asyncio.gather(
            self.weather_service.get_weather(
                latitude,
                longitude,
                request.start_date,
                request.end_date,
            ),
            self.aqi_service.get_aqi(latitude, longitude),
            self.youtube_service.get_travel_videos(request.location),
            return_exceptions=True,
        )

        # Handle exceptions from parallel tasks
        if isinstance(weather_data, Exception):
            logger.warning(f"Failed to fetch weather data: {weather_data}")
            weather_data = None

        if isinstance(aqi, Exception):
            logger.warning(f"Failed to fetch AQI data: {aqi}")
            aqi = None

        if isinstance(videos, Exception):
            logger.warning(f"Failed to fetch YouTube videos: {videos}")
            videos = None

        # Create database record
        weather_request = WeatherRequest(
            location_name=request.location,
            latitude=latitude,
            longitude=longitude,
            start_date=request.start_date,
            end_date=request.end_date,
            weather_data=weather_data,
            aqi=aqi,
            youtube_videos=[v.model_dump() for v in videos] if videos else None,
            extra_metadata={
                "created_by": "api",
                "enriched_at": datetime.utcnow().isoformat(),
            },
        )

        created = await self.repository.create(weather_request)
        await self.session.commit()

        logger.info(f"Created weather request: {created.id}")
        return WeatherResponse.model_validate(created)

    async def get_weather_request(self, request_id: UUID) -> WeatherResponse:
        """Get a weather request by ID."""
        weather_request = await self.repository.get_by_id(request_id)
        if not weather_request:
            raise ResourceNotFoundException("WeatherRequest", str(request_id))

        return WeatherResponse.model_validate(weather_request)

    async def get_all_weather_requests(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[WeatherResponse], int]:
        """Get all weather requests with pagination."""
        requests, total = await self.repository.get_all(skip, limit)
        return (
            [WeatherResponse.model_validate(r) for r in requests],
            total,
        )

    async def search_by_location(
        self,
        location: str,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[WeatherResponse], int]:
        """Search weather requests by location."""
        requests, total = await self.repository.get_by_location(location, skip, limit)
        return (
            [WeatherResponse.model_validate(r) for r in requests],
            total,
        )

    async def update_weather_request(
        self,
        request_id: UUID,
        update_request: WeatherUpdateRequest,
    ) -> WeatherResponse:
        """Update a weather request."""
        existing = await self.repository.get_by_id(request_id)
        if not existing:
            raise ResourceNotFoundException("WeatherRequest", str(request_id))

        # Prepare update data
        update_data: dict[str, Any] = {}

        if update_request.location is not None:
            update_data["location_name"] = update_request.location
            # Re-resolve coordinates if location changed
            latitude, longitude = await self.geocoding_service.resolve_location(
                update_request.location
            )
            update_data["latitude"] = latitude
            update_data["longitude"] = longitude

        if update_request.start_date is not None:
            update_data["start_date"] = update_request.start_date

        if update_request.end_date is not None:
            update_data["end_date"] = update_request.end_date

        updated = await self.repository.update(request_id, **update_data)
        await self.session.commit()

        logger.info(f"Updated weather request: {request_id}")
        return WeatherResponse.model_validate(updated)

    async def delete_weather_request(self, request_id: UUID) -> bool:
        """Delete a weather request."""
        existing = await self.repository.get_by_id(request_id)
        if not existing:
            raise ResourceNotFoundException("WeatherRequest", str(request_id))

        deleted = await self.repository.delete(request_id)
        await self.session.commit()

        logger.info(f"Deleted weather request: {request_id}")
        return deleted

    async def cleanup_old_records(self, days: int = 30) -> int:
        """Delete records older than specified days."""
        deleted_count = await self.repository.delete_old_records(days)
        await self.session.commit()

        logger.info(f"Deleted {deleted_count} old weather requests")
        return deleted_count

    async def list_locations(self, country: str | None = None) -> list[str]:
        """Return a list of distinct stored locations.

        If `country` is provided (e.g., 'IN'), attempt to filter locations by country.
        """
        if country:
            return await self.repository.get_locations_by_country(country)
        return await self.repository.get_distinct_locations()
