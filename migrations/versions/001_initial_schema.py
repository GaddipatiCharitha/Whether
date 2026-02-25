"""Initial migration: Create weather_requests table.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-02-24 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial schema."""
    op.create_table(
        "weather_requests",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("location_name", sa.String(255), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=False),
        sa.Column("weather_data", sa.JSON(), nullable=True),
        sa.Column("aqi", sa.Integer(), nullable=True),
        sa.Column("youtube_videos", sa.JSON(), nullable=True),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_weather_requests_location_name",
        "weather_requests",
        ["location_name"],
    )
    op.create_index(
        "ix_weather_requests_created_at",
        "weather_requests",
        ["created_at"],
    )


def downgrade() -> None:
    """Drop weather_requests table."""
    op.drop_index("ix_weather_requests_created_at", table_name="weather_requests")
    op.drop_index("ix_weather_requests_location_name", table_name="weather_requests")
    op.drop_table("weather_requests")
