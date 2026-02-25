"""API request and response schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class LocationInput(BaseModel):
    """Location input for weather requests."""

    location: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Location name (e.g., 'New York', 'San Francisco')",
    )

    @field_validator("location")
    @classmethod
    def validate_location(cls, v: str) -> str:
        """Validate location string."""
        if not v.strip():
            raise ValueError("Location cannot be empty")
        return v.strip()


class DateRangeInput(BaseModel):
    """Date range input for weather requests."""

    start_date: datetime = Field(..., description="Start date for weather data")
    end_date: datetime = Field(..., description="End date for weather data")

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: datetime, info: Any) -> datetime:
        """Validate that end_date is after start_date."""
        if "start_date" in info.data:
            if v <= info.data["start_date"]:
                raise ValueError("End date must be after start date")
        return v


class WeatherRequestCreate(LocationInput, DateRangeInput):
    """Schema for creating a weather request."""

    class Config:
        json_schema_extra = {
            "example": {
                "location": "San Francisco",
                "start_date": "2026-01-15T00:00:00",
                "end_date": "2026-01-20T00:00:00",
            }
        }


class WeatherDataResponse(BaseModel):
    """Weather data response model."""

    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[str] = None
    description: Optional[str] = None
    precipitation: Optional[float] = None


class YouTubeVideo(BaseModel):
    """YouTube video metadata."""

    video_id: str
    title: str
    channel: str
    published_at: str
    views: Optional[int] = None


class WeatherResponseBase(BaseModel):
    """Base weather response schema."""

    location_name: str
    latitude: float
    longitude: float
    start_date: datetime
    end_date: datetime
    weather_data: Optional[dict[str, Any]] = None
    aqi: Optional[int] = None
    youtube_videos: Optional[list[YouTubeVideo]] = None
    extra_metadata: Optional[dict[str, Any]] = None


class WeatherResponse(WeatherResponseBase):
    """Complete weather response schema."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WeatherUpdateRequest(BaseModel):
    """Schema for updating a weather request."""

    location: Optional[str] = Field(None, min_length=2, max_length=255)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "location": "Los Angeles",
                "start_date": "2026-02-01T00:00:00",
            }
        }


class PaginationParams(BaseModel):
    """Pagination parameters."""

    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(50, ge=1, le=1000, description="Number of records to return")


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""

    total: int
    skip: int
    limit: int
    items: list[WeatherResponse]


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str = "operational"
    environment: str
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    message: str
    details: Optional[dict[str, Any]] = None
