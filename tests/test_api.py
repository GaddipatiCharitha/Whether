"""Tests for weather API endpoints."""

import pytest
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "environment" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Weather API"
        assert "version" in data


@pytest.mark.asyncio
async def test_swagger_docs():
    """Test OpenAPI/Swagger documentation availability."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/docs")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_weather_list_empty():
    """Test listing weather requests when empty."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/weather")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
