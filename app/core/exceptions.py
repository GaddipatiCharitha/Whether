"""Custom exception classes for the application."""

from typing import Any, Optional

from fastapi import HTTPException, status


class ApplicationException(Exception):
    """Base exception for all application exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        return HTTPException(
            status_code=self.status_code,
            detail={
                "error": self.error_code,
                "message": self.message,
                "details": self.details,
            },
        )


class ValidationException(ApplicationException):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class ResourceNotFoundException(ApplicationException):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        resource_type: str = "Resource",
        resource_id: Optional[str] = None,
    ) -> None:
        message = f"{resource_type} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class ExternalAPIException(ApplicationException):
    """Raised when external API calls fail."""

    def __init__(
        self,
        service_name: str,
        message: str = "External API error",
        original_error: Optional[str] = None,
    ) -> None:
        super().__init__(
            message=f"{service_name}: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="EXTERNAL_API_ERROR",
            details={"service": service_name, "original_error": original_error},
        )


class DatabaseException(ApplicationException):
    """Raised when database operations fail."""

    def __init__(
        self,
        message: str = "Database operation failed",
        original_error: Optional[str] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details={"original_error": original_error},
        )


class ConflictException(ApplicationException):
    """Raised when a resource conflict occurs."""

    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT_ERROR",
            details=details,
        )


class LocationResolutionException(ApplicationException):
    """Raised when location cannot be resolved to coordinates."""

    def __init__(self, location: str) -> None:
        super().__init__(
            message=f"Could not resolve location '{location}' to coordinates",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="LOCATION_RESOLUTION_FAILED",
            details={"location": location},
        )
