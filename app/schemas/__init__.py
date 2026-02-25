"""API schemas."""

from app.schemas.weather import (
    DateRangeInput,
    ErrorResponse,
    HealthCheckResponse,
    LocationInput,
    PaginatedResponse,
    PaginationParams,
    WeatherDataResponse,
    WeatherRequestCreate,
    WeatherResponse,
    WeatherResponseBase,
    WeatherUpdateRequest,
    YouTubeVideo,
)

__all__ = [
    "LocationInput",
    "DateRangeInput",
    "WeatherRequestCreate",
    "WeatherResponse",
    "WeatherResponseBase",
    "WeatherUpdateRequest",
    "WeatherDataResponse",
    "YouTubeVideo",
    "PaginationParams",
    "PaginatedResponse",
    "HealthCheckResponse",
    "ErrorResponse",
]
