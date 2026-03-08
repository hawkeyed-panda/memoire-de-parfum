from datetime import datetime
from typing import Optional


def log_graph_retrieval(
    emotions: list[str],
    candidates_found: dict,
    excluded_notes: list[str],
) -> None:
    """Log GraphRAG retrieval results."""
    print(f"[GraphRAG] {datetime.utcnow().isoformat()}")
    print(f"  Emotions queried: {emotions}")
    print(f"  Top candidates: {candidates_found.get('top_candidates', [])}")
    print(f"  Heart candidates: {candidates_found.get('heart_candidates', [])}")
    print(f"  Base candidates: {candidates_found.get('base_candidates', [])}")
    print(f"  Excluded (safety): {excluded_notes}")


def log_substitution_applied(
    original_note: str,
    substitute_note: str,
    reason: str,
) -> None:
    """Log when a safety substitution is applied."""
    print(f"[Guardrail] Substitution applied: {original_note} → {substitute_note} ({reason})")


def log_blueprint_output(
    top_notes: list[str],
    heart_notes: list[str],
    base_notes: list[str],
    intensity: str,
    substitutions: list[str],
) -> None:
    """Log the final blueprint before LLM synthesis."""
    print(f"[Blueprint] {datetime.utcnow().isoformat()}")
    print(f"  Top: {top_notes}")
    print(f"  Heart: {heart_notes}")
    print(f"  Base: {base_notes}")
    print(f"  Intensity: {intensity}")
    print(f"  Substitutions: {substitutions or 'None'}")


def log_cache_hit(cache_key: str) -> None:
    """Log when a cache hit occurs."""
    print(f"[Cache] HIT → key: {cache_key}")


def log_cache_miss(cache_key: str) -> None:
    """Log when a cache miss occurs."""
    print(f"[Cache] MISS → key: {cache_key}")


def log_pipeline_complete(
    memory_frame: str,
    duration_ms: float,
    cache_hit: bool,
) -> None:
    """Log pipeline completion with timing."""
    print(f"[Pipeline] Complete")
    print(f"  Frame: {memory_frame}")
    print(f"  Duration: {duration_ms:.2f}ms")
    print(f"  Cache hit: {cache_hit}")
