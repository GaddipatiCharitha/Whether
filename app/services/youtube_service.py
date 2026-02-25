"""YouTube videos service for location-based content."""

from typing import Any, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.external_api import ExternalAPIClient
from app.schemas.weather import YouTubeVideo
from app.utils.cache import TTLCache

logger = get_logger(__name__)

# Global cache for YouTube videos
youtube_cache: TTLCache = TTLCache(max_size=300, default_ttl=86400)


class YouTubeService:
    """Service for fetching travel videos from YouTube."""

    def __init__(self) -> None:
        self.api_key = settings.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com"

    async def get_travel_videos(
        self,
        location: str,
        max_results: int = 5,
    ) -> list[YouTubeVideo]:
        """Get travel videos for a location."""
        cache_key = f"youtube:{location}:{max_results}"
        cached = await youtube_cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for YouTube videos: {location}")
            return cached

        try:
            async with ExternalAPIClient(
                name="YouTube",
                base_url=self.base_url,
            ) as client:
                result = await client.get(
                    "/youtube/v3/search",
                    params={
                        "q": f"travel guide {location}",
                        "part": "snippet",
                        "maxResults": max_results,
                        "type": "video",
                        "order": "relevance",
                        "key": self.api_key,
                    },
                )

                videos: list[YouTubeVideo] = []
                for item in result.get("items", []):
                    snippet = item.get("snippet", {})
                    video = YouTubeVideo(
                        video_id=item.get("id", {}).get("videoId", ""),
                        title=snippet.get("title", ""),
                        channel=snippet.get("channelTitle", ""),
                        published_at=snippet.get("publishedAt", ""),
                    )
                    videos.append(video)

                await youtube_cache.set(
                    cache_key,
                    videos,
                    ttl_seconds=86400,
                )

                logger.info(f"Fetched {len(videos)} YouTube videos for {location}")
                return videos

        except Exception as e:
            logger.warning(f"Failed to fetch YouTube videos: {str(e)}")
            return []

    async def get_video_stats(self, video_id: str) -> Optional[dict[str, Any]]:
        """Get statistics for a specific video."""
        try:
            async with ExternalAPIClient(
                name="YouTube",
                base_url=self.base_url,
            ) as client:
                result = await client.get(
                    "/youtube/v3/videos",
                    params={
                        "id": video_id,
                        "part": "statistics",
                        "key": self.api_key,
                    },
                )

                if result.get("items"):
                    return result["items"][0].get("statistics", {})

                return None

        except Exception as e:
            logger.warning(f"Failed to fetch video stats: {str(e)}")
            return None
