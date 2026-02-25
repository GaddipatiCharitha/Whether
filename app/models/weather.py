"""Weather data models."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, func

from app.db.base import Base


class WeatherRequest(Base):
    """Weather request data model."""

    __tablename__ = "weather_requests"

    # ✅ Cross-database UUID (SQLite + Postgres safe)
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    location_name = Column(String(255), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    weather_data = Column(JSON, nullable=True)
    aqi = Column(Integer, nullable=True)
    youtube_videos = Column(JSON, nullable=True)

    # ✅ FIX: renamed (metadata is RESERVED)
    extra_metadata = Column(JSON, nullable=True)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<WeatherRequest("
            f"id={self.id}, "
            f"location={self.location_name}, "
            f"lat={self.latitude}, "
            f"lon={self.longitude})>"
        )