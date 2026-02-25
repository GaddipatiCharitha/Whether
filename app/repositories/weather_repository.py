"""Weather data repository."""

from typing import Optional
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weather import WeatherRequest


class WeatherRepository:
    """Repository for weather data access."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, weather_request: WeatherRequest) -> WeatherRequest:
        """Create a new weather request record."""
        self.session.add(weather_request)
        await self.session.flush()
        return weather_request

    async def get_by_id(self, request_id: UUID) -> Optional[WeatherRequest]:
        """Get weather request by ID."""
        stmt = select(WeatherRequest).where(WeatherRequest.id == request_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int = 0, limit: int = 50
    ) -> tuple[list[WeatherRequest], int]:
        """Get all weather requests with pagination."""
        count_stmt = select(func.count()).select_from(WeatherRequest)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = (
            select(WeatherRequest)
            .order_by(WeatherRequest.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all(), total

    async def get_by_location(
        self,
        location_name: str,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[WeatherRequest], int]:
        """Get weather requests by location."""
        count_stmt = select(func.count()).select_from(WeatherRequest).where(
            WeatherRequest.location_name.ilike(f"%{location_name}%")
        )
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = (
            select(WeatherRequest)
            .where(WeatherRequest.location_name.ilike(f"%{location_name}%"))
            .order_by(WeatherRequest.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all(), total

    async def get_distinct_locations(self) -> list[str]:
        """Return distinct location names."""
        stmt = select(WeatherRequest.location_name).distinct().order_by(
            WeatherRequest.location_name
        )
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_locations_by_country(self, country_code: str) -> list[str]:
        """Return distinct location names filtered by country bounding box.

        Currently supports 'IN' (India) using a simple lat/lon bounding box.
        """
        country_code = (country_code or "").upper()
        if country_code == "IN":
            # Rough bounding box for India
            min_lat, max_lat = 6.5, 35.7
            min_lon, max_lon = 68.1, 97.4
            stmt = (
                select(WeatherRequest.location_name)
                .distinct()
                .where(
                    WeatherRequest.latitude.between(min_lat, max_lat),
                    WeatherRequest.longitude.between(min_lon, max_lon),
                )
                .order_by(WeatherRequest.location_name)
            )
            result = await self.session.execute(stmt)
            return [row[0] for row in result.all()]

        # Fallback to all distinct locations
        return await self.get_distinct_locations()

    async def update(self, request_id: UUID, **kwargs: dict) -> Optional[WeatherRequest]:
        """Update a weather request."""
        weather_request = await self.get_by_id(request_id)
        if not weather_request:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(weather_request, key):
                setattr(weather_request, key, value)

        await self.session.flush()
        return weather_request

    async def delete(self, request_id: UUID) -> bool:
        """Delete a weather request."""
        stmt = delete(WeatherRequest).where(WeatherRequest.id == request_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def delete_old_records(self, days: int = 30) -> int:
        """Delete records older than specified days."""
        from datetime import datetime, timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        stmt = delete(WeatherRequest).where(WeatherRequest.created_at < cutoff_date)
        result = await self.session.execute(stmt)
        return result.rowcount
