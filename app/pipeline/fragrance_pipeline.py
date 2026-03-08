import json
from langsmith import traceable

from app.core.signal_extraction import extract_scent_signals
from app.core.constraint_selector import select_fragrance_blueprint
from app.core.llm_synthesis import synthesize_fragrance_output
from app.graph.graph_rag import get_note_candidates
from app.rag.doc_rag import retrieve_references
from app.cache.redis_client import get_cached, set_cached
from app.cache.cache_keys import blueprint_cache_key
from app.models.intent import MemoryFrame, ScentIntentJSON
from app.models.blueprint import FragranceBlueprintJSON
from app.errors.exceptions import MemoireBaseException


@traceable(name="fragrance_pipeline")
async def run_fragrance_pipeline(
    memory_frame: MemoryFrame,
    questionnaire_data: dict,
    free_text_memory: str = ""
) -> dict:
    """
    Master pipeline — runs all steps in sequence.
    Returns the final blueprint + synthesis text.

    Flow:
    1. Signal Extraction   → ScentIntentJSON
    2. GraphRAG            → note candidates from Neo4j
    3. Constraint Selector → FragranceBlueprintJSON
    4. Doc RAG             → retrieved references from Weaviate
    5. LLM Synthesis       → final fragrance story
    """
    try:
        # Step 1 — Signal Extraction
        intent = await extract_scent_signals(
            memory_frame=memory_frame,
            questionnaire_data=questionnaire_data,
            free_text_memory=free_text_memory,
        )

        # Check cache — same intent = return cached result instantly
        cache_key = blueprint_cache_key(intent)
        cached = await get_cached(cache_key)
        if cached:
            return json.loads(cached)

        # Debug: log extracted emotions so we can trace graph mismatches
        print(f"[Pipeline] Extracted emotions: {intent.emotions}")
        print(f"[Pipeline] Intensity: {intent.desired_intensity}, Sensitivity: {intent.skin_sensitivity_constraint}")

        # Step 2 — GraphRAG (Neo4j knowledge graph)
        graph_candidates = await get_note_candidates(intent)
        print(f"[Pipeline] Graph candidates: {graph_candidates}")

        # Step 3 — Constraint Selector + guardrails
        blueprint = select_fragrance_blueprint(
            intent=intent,
            graph_candidates=graph_candidates,
        )

        # Step 4 — Doc RAG (Weaviate vector retrieval)
        retrieved_references = await retrieve_references(blueprint)

        # Step 5 — LLM Synthesis + guardrails
        fragrance_story = await synthesize_fragrance_output(
            intent=intent,
            blueprint=blueprint,
            retrieved_references=retrieved_references,
        )

        # Build final response
        result = {
            "intent": intent.model_dump(),
            "blueprint": blueprint.model_dump(),
            "fragrance_story": fragrance_story,
        }

        # Cache the result
        await set_cached(cache_key, json.dumps(result))

        return result

    except MemoireBaseException:
        raise
    except Exception as e:
        raise MemoireBaseException(
            message=f"Pipeline failed unexpectedly: {str(e)}"
        )


NOTE_LAYER_MAP = {
    "bergamot": "top", "neroli": "top", "pink pepper": "top",
    "black pepper": "top",
    "rose": "heart", "jasmine": "heart", "geranium": "heart",
    "lavender": "heart",
    "sandalwood": "base", "vetiver": "base", "vanilla": "base",
    "patchouli": "base", "cedarwood": "base", "amber": "base",
}

REFINEMENT_INTENSITY_MAP = {
    "lighter": "soft",
    "stronger": "rich",
    "warmer": "rich",
    "fresher": "soft",
}

REFINEMENT_DIRECTION_MAP = {
    "warmer": ["vanilla", "amber", "sandalwood", "patchouli"],
    "fresher": ["bergamot", "neroli", "lavender", "geranium"],
    "lighter": ["neroli", "geranium", "bergamot"],
    "stronger": ["vetiver", "patchouli", "amber", "cedarwood"],
}


def _apply_refinement_to_candidates(
    graph_candidates: dict,
    refinement: str,
) -> dict:
    """
    Reorders and injects notes into graph candidates based on the
    refinement direction so the constraint selector picks different notes.
    """
    direction_notes = REFINEMENT_DIRECTION_MAP.get(refinement, [])
    if not direction_notes:
        return graph_candidates

    top = list(graph_candidates.get("top_candidates", []))
    heart = list(graph_candidates.get("heart_candidates", []))
    base = list(graph_candidates.get("base_candidates", []))

    for note in direction_notes:
        layer = NOTE_LAYER_MAP.get(note)
        if layer == "top":
            if note not in top:
                top.insert(0, note)
            else:
                top.remove(note)
                top.insert(0, note)
        elif layer == "heart":
            if note not in heart:
                heart.insert(0, note)
            else:
                heart.remove(note)
                heart.insert(0, note)
        elif layer == "base":
            if note not in base:
                base.insert(0, note)
            else:
                base.remove(note)
                base.insert(0, note)

    return {
        "top_candidates": top[:5],
        "heart_candidates": heart[:5],
        "base_candidates": base[:5],
        "excluded": graph_candidates.get("excluded", []),
    }


@traceable(name="refinement_pipeline")
async def run_refinement_pipeline(
    existing_intent: ScentIntentJSON,
    refinement: str,
) -> dict:
    """
    Handles refinement requests — lighter, stronger, warmer, fresher.
    Re-runs from GraphRAG onwards (skips signal extraction).
    Injects direction-appropriate notes into candidates before selection.
    """
    try:
        if refinement in REFINEMENT_INTENSITY_MAP:
            existing_intent.desired_intensity = REFINEMENT_INTENSITY_MAP[refinement]

        graph_candidates = await get_note_candidates(existing_intent)

        graph_candidates = _apply_refinement_to_candidates(
            graph_candidates, refinement
        )

        blueprint = select_fragrance_blueprint(
            intent=existing_intent,
            graph_candidates=graph_candidates,
        )

        retrieved_references = await retrieve_references(blueprint)

        fragrance_story = await synthesize_fragrance_output(
            intent=existing_intent,
            blueprint=blueprint,
            retrieved_references=retrieved_references,
        )

        return {
            "intent": existing_intent.model_dump(),
            "blueprint": blueprint.model_dump(),
            "fragrance_story": fragrance_story,
            "refinement_applied": refinement,
        }

    except MemoireBaseException:
        raise
    except Exception as e:
        raise MemoireBaseException(
            message=f"Refinement pipeline failed: {str(e)}"
        )
