"""Pagination utilities."""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams:
    """Pagination parameters."""

    def __init__(self, skip: int = 0, limit: int = 50) -> None:
        self.skip = max(0, skip)
        self.limit = max(1, min(limit, 1000))  # Max 1000 items per page


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response."""

    total: int
    skip: int
    limit: int
    items: list[T]

    @property
    def total_pages(self) -> int:
        """Calculate total pages."""
        if self.limit == 0:
            return 0
        return (self.total + self.limit - 1) // self.limit

    @property
    def current_page(self) -> int:
        """Calculate current page number."""
        if self.limit == 0:
            return 0
        return (self.skip // self.limit) + 1

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return (self.skip + self.limit) < self.total

    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.skip > 0
