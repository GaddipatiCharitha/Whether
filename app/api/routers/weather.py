"""Weather API routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ApplicationException, ResourceNotFoundException
from app.core.logging import get_logger
from app.db import get_session
from app.exports.weather_export import ExportService
from app.schemas.weather import (
    PaginatedResponse,
    WeatherRequestCreate,
    WeatherResponse,
    WeatherUpdateRequest,
)
from app.services.weather_application_service import WeatherApplicationService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/weather", tags=["weather"])


@router.get(
    "/locations",
    response_model=list[str],
    summary="List distinct locations",
    description="Return distinct stored location names",
)
async def list_locations(
    country: Optional[str] = Query(None, description="Optional ISO country code to filter locations"),
    session: AsyncSession = Depends(get_session),
) -> list[str]:
    try:
        service = WeatherApplicationService(session)
        return await service.list_locations(country)
    except Exception as e:
        logger.error(f"Error listing locations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list locations",
        )


@router.post(
    "",
    response_model=WeatherResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Weather Request",
    description="Create a new weather request with location, date range, and enriched data",
)
async def create_weather(
    request: WeatherRequestCreate,
    session: AsyncSession = Depends(get_session),
) -> WeatherResponse:
    """Create a new weather request.

    Enriches with:
    - Location coordinates (geocoding)
    - Weather data
    - Air Quality Index
    - Travel videos
    """
    try:
        service = WeatherApplicationService(session)
        return await service.create_weather_request(request)
    except ApplicationException as e:
        raise e.to_http_exception()
    except Exception as e:
        logger.error(f"Error creating weather request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create weather request",
        )


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="List Weather Requests",
    description="Get all weather requests with pagination",
)
async def list_weather(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Number of records to return"),
    session: AsyncSession = Depends(get_session),
) -> PaginatedResponse:
    """Get all weather requests with pagination."""
    try:
        service = WeatherApplicationService(session)
        items, total = await service.get_all_weather_requests(skip, limit)
        return PaginatedResponse(total=total, skip=skip, limit=limit, items=items)
    except Exception as e:
        logger.error(f"Error listing weather requests: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list weather requests",
        )


@router.get(
    "/search",
    response_model=PaginatedResponse,
    summary="Search by Location",
    description="Search weather requests by location name",
)
async def search_by_location(
    location: str = Query(..., min_length=2, description="Location name to search"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
) -> PaginatedResponse:
    """Search weather requests by location."""
    try:
        service = WeatherApplicationService(session)
        items, total = await service.search_by_location(location, skip, limit)
        return PaginatedResponse(total=total, skip=skip, limit=limit, items=items)
    except Exception as e:
        logger.error(f"Error searching by location: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search weather requests",
        )


@router.get(
    "/{request_id}",
    response_model=WeatherResponse,
    summary="Get Weather Request",
    description="Get a specific weather request by ID",
)
async def get_weather(
    request_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> WeatherResponse:
    """Get a specific weather request."""
    try:
        service = WeatherApplicationService(session)
        return await service.get_weather_request(request_id)
    except ResourceNotFoundException as e:
        raise e.to_http_exception()
    except Exception as e:
        logger.error(f"Error getting weather request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get weather request",
        )


@router.put(
    "/{request_id}",
    response_model=WeatherResponse,
    summary="Update Weather Request",
    description="Update an existing weather request",
)
async def update_weather(
    request_id: UUID,
    update_request: WeatherUpdateRequest,
    session: AsyncSession = Depends(get_session),
) -> WeatherResponse:
    """Update a weather request."""
    try:
        service = WeatherApplicationService(session)
        return await service.update_weather_request(request_id, update_request)
    except ResourceNotFoundException as e:
        raise e.to_http_exception()
    except ApplicationException as e:
        raise e.to_http_exception()
    except Exception as e:
        logger.error(f"Error updating weather request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update weather request",
        )


@router.delete(
    "/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Weather Request",
    description="Delete a weather request by ID",
)
async def delete_weather(
    request_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a weather request."""
    try:
        service = WeatherApplicationService(session)
        await service.delete_weather_request(request_id)
    except ResourceNotFoundException as e:
        raise e.to_http_exception()
    except Exception as e:
        logger.error(f"Error deleting weather request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete weather request",
        )


@router.get(
    "/{request_id}/export/json",
    summary="Export as JSON",
    description="Export a weather request as JSON",
    responses={200: {"content": {"application/json": {}}}},
)
async def export_json(
    request_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Export weather request as JSON."""
    try:
        service = WeatherApplicationService(session)
        weather = await service.get_weather_request(request_id)
        json_data = ExportService.to_json([weather])
        return {"data": json_data}
    except ResourceNotFoundException as e:
        raise e.to_http_exception()
    except Exception as e:
        logger.error(f"Error exporting JSON: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export JSON",
        )


@router.get(
    "/{request_id}/export/csv",
    summary="Export as CSV",
    description="Export a weather request as CSV",
    responses={200: {"content": {"text/csv": {}}}},
)
async def export_csv(
    request_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Export weather request as CSV."""
    try:
        service = WeatherApplicationService(session)
        weather = await service.get_weather_request(request_id)
        csv_data = ExportService.to_csv([weather])
        return {"data": csv_data}
    except ResourceNotFoundException as e:
        raise e.to_http_exception()
    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export CSV",
        )


@router.get(
    "/{request_id}/export/pdf",
    summary="Export as PDF",
    description="Export a weather request as PDF",
    responses={200: {"content": {"application/pdf": {}}}},
)
async def export_pdf(
    request_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Export weather request as PDF."""
    try:
        service = WeatherApplicationService(session)
        weather = await service.get_weather_request(request_id)
        pdf_data = ExportService.to_pdf([weather])
        import base64
        return {"data": base64.b64encode(pdf_data).decode()}
    except ResourceNotFoundException as e:
        raise e.to_http_exception()
    except Exception as e:
        logger.error(f"Error exporting PDF: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export PDF",
        )
