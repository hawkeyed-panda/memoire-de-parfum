from langsmith import traceable
from app.models.intent import ScentIntentJSON, SkinSensitivity
from app.graph.neo4j_client import run_query
from app.errors.exceptions import GraphRAGError


@traceable(name="graph_rag")
async def get_note_candidates(intent: ScentIntentJSON) -> dict:
    """
    Queries the Neo4j knowledge graph using emotions from ScentIntentJSON.
    Returns candidate notes per layer — top, heart, base.
    Applies sensitivity-based exclusions from the graph.
    """
    try:
        emotions = intent.emotions or []
        sensitivity = intent.skin_sensitivity_constraint or SkinSensitivity.BALANCED

        # Step 1 — get notes evoked by the user's emotions
        emotion_query = """
        MATCH (e:Emotion)-[:EVOKES]->(n:Note)
        WHERE e.name IN $emotions
        RETURN n.name AS name, n.layer AS layer, n.family AS family,
               COUNT(e) AS emotion_match_count
        ORDER BY emotion_match_count DESC
        """
        emotion_results = await run_query(
            emotion_query,
            {"emotions": emotions}
        )

        # Step 2 — get safety flags to exclude
        severity_filter = _get_severity_filter(sensitivity)
        safety_query = """
        MATCH (s:SafetyFlag)
        WHERE s.severity IN $severities
        RETURN s.name AS banned_note
        """
        safety_results = await run_query(
            safety_query,
            {"severities": severity_filter}
        )
        banned_notes = {r["banned_note"] for r in safety_results}

        # Step 3 — separate by layer, exclude banned notes, deduplicate
        top_candidates = []
        heart_candidates = []
        base_candidates = []
        seen = set()

        for record in emotion_results:
            note_name = record["name"]
            if note_name in banned_notes or note_name in seen:
                continue
            seen.add(note_name)
            if record["layer"] == "top":
                top_candidates.append(note_name)
            elif record["layer"] == "heart":
                heart_candidates.append(note_name)
            elif record["layer"] == "base":
                base_candidates.append(note_name)

        # Step 4 — fallback if any layer is empty
        top_candidates = top_candidates or ["bergamot"]
        heart_candidates = heart_candidates or ["rose"]
        base_candidates = base_candidates or ["sandalwood"]

        return {
            "top_candidates": top_candidates[:5],
            "heart_candidates": heart_candidates[:5],
            "base_candidates": base_candidates[:5],
            "excluded": list(banned_notes),
        }

    except Exception as e:
        raise GraphRAGError(
            message=f"GraphRAG query failed: {str(e)}"
        )


def _get_severity_filter(sensitivity: SkinSensitivity) -> list[str]:
    """
    Maps skin sensitivity to which severity levels to exclude.
    Very gentle → exclude all severities.
    Balanced → exclude high + medium.
    Expressive → exclude only high.
    """
    if sensitivity == SkinSensitivity.VERY_GENTLE:
        return ["high", "medium", "low"]
    elif sensitivity == SkinSensitivity.BALANCED:
        return ["high", "medium"]
    else:
        return ["high"]
