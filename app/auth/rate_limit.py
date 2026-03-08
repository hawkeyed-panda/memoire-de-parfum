from fastapi import Request
from app.cache.redis_client import get_redis_client
from app.config import settings
from app.errors.exceptions import RateLimitExceededError


async def check_rate_limit(request: Request) -> None:
    """
    Per-user rate limiter using Redis.
    Tracks requests per minute per IP or user.
    Raises RateLimitExceededError if limit is exceeded.
    """
    # Use user ID from token if available, otherwise fall back to IP
    user_id = getattr(request.state, "user_id", None)
    identifier = user_id or request.client.host

    key = f"rate_limit:{identifier}"

    try:
        client = await get_redis_client()

        # Increment request count
        count = await client.incr(key)

        # Set expiry on first request
        if count == 1:
            await client.expire(key, 60)  # 60 second window

        if count > settings.RATE_LIMIT_PER_MINUTE:
            raise RateLimitExceededError()

    except RateLimitExceededError:
        raise
    except Exception:
        pass  # Redis failure — fail open, don't block the request
