import time
from contextlib import asynccontextmanager
from app.cache.redis_client import get_redis_client


@asynccontextmanager
async def track_latency(step_name: str):
    """
    Context manager that tracks latency for a pipeline step.
    Usage:
        async with track_latency("signal_extraction"):
            result = await extract_scent_signals(...)
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        await _record_latency(step_name, duration_ms)
        print(f"[Latency] {step_name}: {duration_ms:.2f}ms")


async def _record_latency(step_name: str, duration_ms: float) -> None:
    """Store latency sample in Redis for p50/p95 calculation."""
    try:
        client = await get_redis_client()
        key = f"latency:{step_name}"
        await client.lpush(key, duration_ms)
        await client.ltrim(key, 0, 999)   # keep last 1000 samples
    except Exception:
        pass


async def get_latency_stats(step_name: str) -> dict:
    """
    Calculate p50 and p95 latency for a pipeline step
    from stored Redis samples.
    """
    try:
        client = await get_redis_client()
        key = f"latency:{step_name}"
        samples = await client.lrange(key, 0, -1)

        if not samples:
            return {"p50": None, "p95": None, "count": 0}

        values = sorted([float(s) for s in samples])
        count = len(values)
        p50 = values[int(count * 0.50)]
        p95 = values[int(count * 0.95)]

        return {"p50": round(p50, 2), "p95": round(p95, 2), "count": count}

    except Exception:
        return {"p50": None, "p95": None, "count": 0}
