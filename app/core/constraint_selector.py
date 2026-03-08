from langsmith import traceable
from app.models.intent import ScentIntentJSON, SkinSensitivity
from app.models.blueprint import FragranceBlueprintJSON, FragranceNote
from app.errors.exceptions import ConstraintSelectorError
from app.guardrails.safety_rules import apply_safety_rules
from app.guardrails.schema_validator import validate_blueprint_schema


# --- Compatibility rules ---
# Notes that pair well together
COMPATIBLE_PAIRS = {
    "rose": ["sandalwood", "bergamot", "geranium", "vanilla", "vetiver"],
    "bergamot": ["rose", "jasmine", "cedarwood", "vetiver", "neroli"],
    "sandalwood": ["rose", "vanilla", "jasmine", "bergamot", "patchouli"],
    "vanilla": ["sandalwood", "rose", "patchouli", "vetiver", "amber"],
    "vetiver": ["rose", "bergamot", "sandalwood", "cedarwood", "patchouli"],
    "jasmine": ["bergamot", "sandalwood", "rose", "cedarwood", "neroli"],
    "patchouli": ["vanilla", "vetiver", "rose", "sandalwood", "bergamot"],
    "cedarwood": ["bergamot", "jasmine", "vetiver", "sandalwood", "neroli"],
    "neroli": ["bergamot", "jasmine", "cedarwood", "rose", "sandalwood"],
    "geranium": ["rose", "bergamot", "sandalwood", "cedarwood", "lavender"],
    "lavender": ["geranium", "bergamot", "cedarwood", "vanilla", "neroli"],
    "amber": ["vanilla", "sandalwood", "patchouli", "rose", "vetiver"],
}

# Notes to avoid per skin sensitivity level
SENSITIVITY_AVOID = {
    SkinSensitivity.VERY_GENTLE: [
        "oakmoss", "peru balsam", "cinnamon bark",
        "clove", "lemongrass", "ylang ylang"
    ],
    SkinSensitivity.BALANCED: [
        "oakmoss", "peru balsam", "cinnamon bark"
    ],
    SkinSensitivity.EXPRESSIVE: [
        "oakmoss", "peru balsam"       # only the strongest sensitizers
    ],
}

# Safe substitutions for avoided notes
SAFE_SUBSTITUTIONS = {
    "oakmoss": "cedarwood",
    "peru balsam": "vanilla",
    "cinnamon bark": "pink pepper",
    "clove": "black pepper",
    "lemongrass": "bergamot",
    "ylang ylang": "neroli",
}

# Intensity → base note weight mapping
INTENSITY_PROFILE = {
    "soft": {"top": 3, "heart": 2, "base": 1},
    "gentle": {"top": 2, "heart": 2, "base": 2},
    "rich": {"top": 1, "heart": 2, "base": 3},
}


def _apply_substitutions(
    notes: list[str],
    sensitivity: SkinSensitivity
) -> tuple[list[str], list[str]]:
    """
    Replace unsafe notes with safe alternatives.
    Returns (deduplicated cleaned note list, list of substitutions applied).
    """
    avoid_list = SENSITIVITY_AVOID.get(sensitivity, [])
    substitutions_applied = []
    cleaned = []
    seen = set()

    for note in notes:
        if note.lower() in avoid_list:
            substitute = SAFE_SUBSTITUTIONS.get(note.lower(), "sandalwood")
            if substitute not in seen:
                cleaned.append(substitute)
                seen.add(substitute)
            substitutions_applied.append(f"{note} → {substitute}")
        else:
            if note not in seen:
                cleaned.append(note)
                seen.add(note)

    return cleaned, substitutions_applied


def _check_compatibility(top: list[str], heart: list[str], base: list[str]) -> bool:
    """Check that at least one note in each layer is compatible with the others."""
    all_notes = top + heart + base
    for note in all_notes:
        note_lower = note.lower()
        if note_lower in COMPATIBLE_PAIRS:
            compatible = COMPATIBLE_PAIRS[note_lower]
            if any(n.lower() in compatible for n in all_notes if n != note):
                return True
    return False


def _build_fragrance_note(name: str, family: str, description: str,
                           is_substituted: bool = False,
                           substituted_from: str = None) -> FragranceNote:
    return FragranceNote(
        name=name,
        family=family,
        description=description,
        is_substituted=is_substituted,
        substituted_from=substituted_from,
    )


def _get_note_family(note: str) -> str:
    """Simple family classification."""
    floral = ["rose", "jasmine", "neroli", "geranium", "ylang ylang", "lavender"]
    woody = ["sandalwood", "cedarwood", "vetiver", "patchouli"]
    citrus = ["bergamot", "lemongrass", "neroli"]
    oriental = ["vanilla", "amber", "patchouli"]
    spicy = ["pink pepper", "black pepper", "cinnamon bark", "clove"]

    note_lower = note.lower()
    if note_lower in floral:
        return "floral"
    elif note_lower in woody:
        return "woody"
    elif note_lower in citrus:
        return "citrus"
    elif note_lower in oriental:
        return "oriental"
    elif note_lower in spicy:
        return "spicy"
    return "aromatic"


def _get_note_description(note: str, memory_frame: str) -> str:
    """Returns an experiential description tied to the memory frame."""
    descriptions = {
        "rose": {
            "past": "evokes warmth and tender memory",
            "present": "radiates confidence and femininity",
            "future": "embodies timeless elegance",
        },
        "bergamot": {
            "past": "recalls fresh, sunlit moments",
            "present": "energizes and uplifts daily mood",
            "future": "opens the journey with brightness",
        },
        "sandalwood": {
            "past": "grounds the memory in warmth",
            "present": "adds depth and calm presence",
            "future": "leaves a lasting, elegant trail",
        },
        "vanilla": {
            "past": "wraps the memory in softness and comfort",
            "present": "adds a warm, approachable character",
            "future": "creates an intimate, memorable finish",
        },
        "vetiver": {
            "past": "anchors the memory in earthy richness",
            "present": "adds grounded sophistication",
            "future": "leaves a deep, distinctive impression",
        },
    }
    default = f"adds depth and character to the {memory_frame} memory"
    return descriptions.get(note.lower(), {}).get(memory_frame, default)


@traceable(name="constraint_selector")
def select_fragrance_blueprint(
    intent: ScentIntentJSON,
    graph_candidates: dict
) -> FragranceBlueprintJSON:
    """
    Takes ScentIntentJSON + GraphRAG candidates.
    Applies compatibility, intensity, and safety constraints.
    Returns a validated FragranceBlueprintJSON.
    """
    try:
        sensitivity = intent.skin_sensitivity_constraint or SkinSensitivity.BALANCED
        intensity = intent.desired_intensity or "gentle"
        memory_frame = intent.memory_frame.value

        # Step 1 — apply safety substitutions
        top_notes_raw, top_subs = _apply_substitutions(
            graph_candidates.get("top_candidates", []), sensitivity
        )
        heart_notes_raw, heart_subs = _apply_substitutions(
            graph_candidates.get("heart_candidates", []), sensitivity
        )
        base_notes_raw, base_subs = _apply_substitutions(
            graph_candidates.get("base_candidates", []), sensitivity
        )
        all_substitutions = top_subs + heart_subs + base_subs

        # Step 2 — apply intensity profile + deduplicate within and across layers
        profile = INTENSITY_PROFILE.get(intensity, INTENSITY_PROFILE["gentle"])

        def _dedupe(lst):
            seen, out = set(), []
            for n in lst:
                if n not in seen:
                    seen.add(n)
                    out.append(n)
            return out

        top_notes_raw = _dedupe(top_notes_raw)
        heart_notes_raw = _dedupe(heart_notes_raw)
        base_notes_raw = _dedupe(base_notes_raw)

        top_final = top_notes_raw[:profile["top"]]
        used = set(top_final)
        heart_final = [n for n in heart_notes_raw if n not in used][:profile["heart"]]
        used.update(heart_final)
        base_final = [n for n in base_notes_raw if n not in used][:profile["base"]]

        print(f"[Selector] Final notes — top: {top_final}, heart: {heart_final}, base: {base_final}")

        # Step 3 — build FragranceNote objects
        def build_notes(notes, substituted_names):
            result = []
            seen_names = set()
            for note in notes:
                if note in seen_names:
                    continue
                seen_names.add(note)
                original = next(
                    (s.split(" → ")[0] for s in substituted_names
                     if s.endswith(f"→ {note}")), None
                )
                result.append(_build_fragrance_note(
                    name=note,
                    family=_get_note_family(note),
                    description=_get_note_description(note, memory_frame),
                    is_substituted=original is not None,
                    substituted_from=original,
                ))
            return result

        top_note_objects = build_notes(top_final, all_substitutions)
        heart_note_objects = build_notes(heart_final, all_substitutions)
        base_note_objects = build_notes(base_final, all_substitutions)

        # Step 4 — build blueprint
        blueprint = FragranceBlueprintJSON(
            memory_frame=intent.memory_frame,
            top_notes=top_note_objects,
            heart_notes=heart_note_objects,
            base_notes=base_note_objects,
            intensity=intensity,
            projection=_map_sensitivity_to_projection(sensitivity),
            longevity=_map_intensity_to_longevity(intensity),
            skin_sensitivity=sensitivity,
            safety_note=_build_safety_note(sensitivity, all_substitutions),
            substitutions_applied=all_substitutions,
        )

        # Step 5 — run guardrails
        apply_safety_rules(blueprint, sensitivity)
        validate_blueprint_schema(blueprint)

        return blueprint

    except Exception as e:
        raise ConstraintSelectorError(
            message=f"Constraint selection failed: {str(e)}"
        )


def _map_sensitivity_to_projection(sensitivity: SkinSensitivity) -> str:
    mapping = {
        SkinSensitivity.VERY_GENTLE: "skin-close",
        SkinSensitivity.BALANCED: "balanced",
        SkinSensitivity.EXPRESSIVE: "statement",
    }
    return mapping.get(sensitivity, "balanced")


def _map_intensity_to_longevity(intensity: str) -> str:
    mapping = {
        "soft": "subtle",
        "gentle": "evolving",
        "rich": "lasting",
    }
    return mapping.get(intensity, "evolving")


def _build_safety_note(sensitivity: SkinSensitivity, substitutions: list[str]) -> str:
    base = "All notes selected are considered safe for general use."
    if sensitivity == SkinSensitivity.VERY_GENTLE:
        base = "Formulated with extra care for sensitive skin."
    if substitutions:
        subs_text = ", ".join(substitutions)
        base += f" The following substitutions were applied: {subs_text}."
    return base
