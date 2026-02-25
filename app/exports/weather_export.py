"""Data export functionality."""

import csv
import json
from io import BytesIO, StringIO
from typing import Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors

from app.core.logging import get_logger
from app.schemas.weather import WeatherResponse

logger = get_logger(__name__)


class ExportService:
    """Service for exporting weather data."""

    @staticmethod
    def to_json(weather_requests: list[WeatherResponse]) -> str:
        """Export weather requests as JSON."""
        try:
            data = [r.model_dump(mode="json") for r in weather_requests]
            return json.dumps(data, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to export JSON: {str(e)}")
            raise

    @staticmethod
    def to_csv(weather_requests: list[WeatherResponse]) -> str:
        """Export weather requests as CSV."""
        try:
            output = StringIO()
            if not weather_requests:
                return ""

            fieldnames = [
                "id",
                "location_name",
                "latitude",
                "longitude",
                "start_date",
                "end_date",
                "aqi",
                "created_at",
                "updated_at",
            ]

            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            for req in weather_requests:
                writer.writerow({
                    "id": str(req.id),
                    "location_name": req.location_name,
                    "latitude": req.latitude,
                    "longitude": req.longitude,
                    "start_date": req.start_date.isoformat(),
                    "end_date": req.end_date.isoformat(),
                    "aqi": req.aqi or "N/A",
                    "created_at": req.created_at.isoformat(),
                    "updated_at": req.updated_at.isoformat(),
                })

            return output.getvalue()

        except Exception as e:
            logger.error(f"Failed to export CSV: {str(e)}")
            raise

    @staticmethod
    def to_pdf(weather_requests: list[WeatherResponse]) -> bytes:
        """Export weather requests as PDF."""
        try:
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=letter,
                rightMargin=0.5 * inch,
                leftMargin=0.5 * inch,
                topMargin=0.75 * inch,
                bottomMargin=0.75 * inch,
            )

            elements: list[Any] = []
            styles = getSampleStyleSheet()

            # Title
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1E3A8A"),
                spaceAfter=30,
                alignment=1,
            )
            elements.append(Paragraph("Weather Report", title_style))
            elements.append(Spacer(1, 0.3 * inch))

            if not weather_requests:
                elements.append(Paragraph("No weather data to display.", styles["Normal"]))
            else:
                # Create table
                data = [
                    [
                        "Location",
                        "Latitude",
                        "Longitude",
                        "AQI",
                        "Created",
                    ]
                ]

                for req in weather_requests:
                    data.append([
                        req.location_name,
                        f"{req.latitude:.2f}",
                        f"{req.longitude:.2f}",
                        str(req.aqi) if req.aqi else "N/A",
                        req.created_at.strftime("%Y-%m-%d"),
                    ])

                table = Table(data, colWidths=[2 * inch, 1 * inch, 1 * inch, 0.8 * inch, 1.2 * inch])
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]))

                elements.append(table)

            doc.build(elements)
            pdf_buffer.seek(0)
            return pdf_buffer.getvalue()

        except Exception as e:
            logger.error(f"Failed to export PDF: {str(e)}")
            raise
