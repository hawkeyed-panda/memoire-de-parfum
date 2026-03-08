from typing import Optional

import redis.asyncio as redis
from app.config import settings
from app.errors.exceptions import RedisConnectionError


_redis_client = None


async def get_redis_client() -> redis.Redis:
    """Returns a singleton Redis client."""
    global _redis_client

    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True,
            )
            await _redis_client.ping()
        except Exception as e:
            raise RedisConnectionError(
                message=f"Could not connect to Redis: {str(e)}"
            )

    return _redis_client


async def get_cached(key: str) -> Optional[str]:
    """Retrieve a cached value by key. Returns None if not found."""
    try:
        client = await get_redis_client()
        return await client.get(key)
    except Exception:
        return None     # cache miss — fail silently, don't break the pipeline


async def set_cached(key: str, value: str, ttl: int = None) -> None:
    """Store a value in cache with optional TTL."""
    try:
        client = await get_redis_client()
        await client.set(
            key,
            value,
            ex=ttl or settings.REDIS_TTL_SECONDS
        )
    except Exception:
        pass            # cache write failure — fail silently


async def invalidate_cache(key: str) -> None:
    """Delete a cached value."""
    try:
        client = await get_redis_client()
        await client.delete(key)
    except Exception:
        pass


async def close_redis():
    """Close Redis connection on app shutdown."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
