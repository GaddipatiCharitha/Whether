"""Retry logic for API calls."""

import asyncio
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")


class RetryConfig:
    """Configuration for retry logic."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
    ) -> None:
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number."""
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            import random

            delay *= random.uniform(0.8, 1.2)

        return delay


async def retry_with_backoff(
    func: Callable[..., Awaitable[T]],
    *args: Any,
    config: RetryConfig = None,
    **kwargs: Any,
) -> T:
    """Execute async function with exponential backoff retry."""
    if config is None:
        config = RetryConfig()

    last_exception: Exception | None = None

    for attempt in range(config.max_attempts):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < config.max_attempts - 1:
                delay = config.get_delay(attempt)
                await asyncio.sleep(delay)
            continue

    raise last_exception or Exception("Retry function failed")
