"""In-memory caching with TTL support."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")


class CacheEntry(Generic[T]):
    """Cache entry with TTL."""

    def __init__(self, value: T, ttl_seconds: int) -> None:
        self.value = value
        self.created_at = datetime.utcnow()
        self.ttl_seconds = ttl_seconds

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        expiry_time = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.utcnow() > expiry_time


class TTLCache(Generic[T]):
    """In-memory cache with Time-To-Live support."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600) -> None:
        self.cache: dict[str, CacheEntry[T]] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[T]:
        """Get value from cache if not expired."""
        async with self._lock:
            if key not in self.cache:
                return None

            entry = self.cache[key]
            if entry.is_expired():
                del self.cache[key]
                return None

            return entry.value

    async def set(self, key: str, value: T, ttl_seconds: Optional[int] = None) -> None:
        """Set value in cache."""
        async with self._lock:
            # Clean up expired entries if cache is full
            if len(self.cache) >= self.max_size:
                expired_keys = [
                    k for k, v in self.cache.items() if v.is_expired()
                ]
                for k in expired_keys:
                    del self.cache[k]

            # Remove oldest entry if still at capacity
            if len(self.cache) >= self.max_size:
                oldest_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k].created_at,
                )
                del self.cache[oldest_key]

            ttl = ttl_seconds or self.default_ttl
            self.cache[key] = CacheEntry(value, ttl)

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self.cache.clear()

    async def cleanup(self) -> int:
        """Remove all expired entries."""
        async with self._lock:
            expired_keys = [
                k for k, v in self.cache.items() if v.is_expired()
            ]
            for k in expired_keys:
                del self.cache[k]
            return len(expired_keys)
