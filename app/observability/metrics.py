from app.cache.redis_client import get_redis_client


async def increment_metric(metric_name: str) -> None:
    """Increment a counter metric in Redis."""
    try:
        client = await get_redis_client()
        await client.incr(f"metric:{metric_name}")
    except Exception:
        pass


async def get_metric(metric_name: str) -> int:
    """Get current value of a metric."""
    try:
        client = await get_redis_client()
        value = await client.get(f"metric:{metric_name}")
        return int(value) if value else 0
    except Exception:
        return 0


async def track_generation() -> None:
    """Track every time a fragrance is generated."""
    await increment_metric("total_generations")


async def track_cache_hit() -> None:
    """Track cache hits."""
    await increment_metric("cache_hits")


async def track_refinement() -> None:
    """Track every refinement request."""
    await increment_metric("total_refinements")


async def track_save() -> None:
    """Track every time a blend is saved."""
    await increment_metric("total_saves")


async def track_guardrail_violation(violation_type: str) -> None:
    """Track guardrail violations by type."""
    await increment_metric(f"guardrail_violation:{violation_type}")


async def get_all_metrics() -> dict:
    """Returns all tracked metrics — useful for a dashboard."""
    return {
        "total_generations": await get_metric("total_generations"),
        "cache_hits": await get_metric("cache_hits"),
        "total_refinements": await get_metric("total_refinements"),
        "total_saves": await get_metric("total_saves"),
    }
