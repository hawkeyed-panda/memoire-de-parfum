
from datetime import datetime
from app.cache.redis_client import get_redis_client
import json


async def store_feedback(
    user_id: str,
    blend_id: str,
    action: str,                    # "save", "regenerate", "refine", "dismiss"
    refinement: str = None,         # "lighter", "stronger", "warmer", "fresher"
    memory_frame: str = None,
) -> None:
    """
    Stores user feedback signals in Redis.
    These are used to track what users do after receiving a fragrance.
    Feeds into offline evaluation over time.
    """
    try:
        client = await get_redis_client()

        feedback_entry = {
            "user_id": user_id,
            "blend_id": blend_id,
            "action": action,
            "refinement": refinement,
            "memory_frame": memory_frame,
            "timestamp": datetime.utcnow().isoformat(),
        }

        key = f"feedback:{user_id}"
        await client.lpush(key, json.dumps(feedback_entry))
        await client.ltrim(key, 0, 499)   # keep last 500 feedback entries per user

        # Global action counters
        await client.incr(f"feedback_count:{action}")

    except Exception:
        pass   # feedback failure should never break the user experience


async def get_user_feedback(user_id: str) -> list[dict]:
    """Retrieve all feedback entries for a user."""
    try:
        client = await get_redis_client()
        key = f"feedback:{user_id}"
        entries = await client.lrange(key, 0, -1)
        return [json.loads(e) for e in entries]
    except Exception:
        return []


async def get_feedback_summary() -> dict:
    """
    Returns aggregated feedback counts.
    Useful for monitoring what users do most after generation.
    """
    try:
        client = await get_redis_client()
        actions = ["save", "regenerate", "refine", "dismiss"]
        summary = {}
        for action in actions:
            count = await client.get(f"feedback_count:{action}")
            summary[action] = int(count) if count else 0
        return summary
    except Exception:
        return {}
