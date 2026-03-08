import hashlib
import json
from app.models.intent import ScentIntentJSON


def _hash(data: str) -> str:
    """Generate a short deterministic hash from a string."""
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def intent_cache_key(intent: ScentIntentJSON) -> str:
    """
    Generates a deterministic cache key from a ScentIntentJSON.
    Same questionnaire answers = same key = cache hit.
    """
    intent_dict = intent.model_dump(exclude_none=True)
    intent_str = json.dumps(intent_dict, sort_keys=True)
    return f"blueprint:{_hash(intent_str)}"


def blueprint_cache_key(intent: ScentIntentJSON) -> str:
    """Cache key specifically for the full fragrance blueprint."""
    intent_dict = intent.model_dump(exclude_none=True)
    intent_str = json.dumps(intent_dict, sort_keys=True)
    return f"full_blueprint:{_hash(intent_str)}"


def synthesis_cache_key(intent: ScentIntentJSON) -> str:
    """Cache key for the final LLM synthesis output."""
    intent_dict = intent.model_dump(exclude_none=True)
    intent_str = json.dumps(intent_dict, sort_keys=True)
    return f"synthesis:{_hash(intent_str)}"


def user_session_key(user_id: str) -> str:
    """Cache key for a user's active session."""
    return f"session:{user_id}"
