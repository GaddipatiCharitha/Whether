"""Tests for weather application service."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app.schemas.weather import WeatherRequestCreate
from app.services.weather_application_service import WeatherApplicationService


@pytest.mark.asyncio
async def test_create_weather_request_success(test_db):
    """Test successful weather request creation."""
    service = WeatherApplicationService(test_db)

    request = WeatherRequestCreate(
        location="Test City",
        start_date=datetime(2026, 2, 24),
        end_date=datetime(2026, 2, 25),
    )

    with patch.object(
        service.geocoding_service,
        "resolve_location",
        new_callable=AsyncMock,
        return_value=(40.7128, -74.0060),
    ):
        with patch.object(
            service.weather_service,
            "get_weather",
            new_callable=AsyncMock,
            return_value={"temperature": 25, "humidity": 60},
        ):
            with patch.object(
                service.aqi_service,
                "get_aqi",
                new_callable=AsyncMock,
                return_value=2,
            ):
                with patch.object(
                    service.youtube_service,
                    "get_travel_videos",
                    new_callable=AsyncMock,
                    return_value=[],
                ):
                    result = await service.create_weather_request(request)

                    assert result.location_name == "Test City"
                    assert result.latitude == 40.7128
                    assert result.longitude == -74.0060
                    assert result.aqi == 2


@pytest.mark.asyncio
async def test_invalid_location(test_db):
    """Test weather request with invalid location."""
    from app.core.exceptions import LocationResolutionException

    service = WeatherApplicationService(test_db)

    request = WeatherRequestCreate(
        location="",
        start_date=datetime(2026, 2, 24),
        end_date=datetime(2026, 2, 25),
    )

    # This should fail validation at schema level
    with pytest.raises(ValueError):
        WeatherRequestCreate(
            location="",
            start_date=datetime(2026, 2, 24),
            end_date=datetime(2026, 2, 25),
        )
