from dataclasses import dataclass
from typing import Optional


@dataclass
class RubricScore:
    relevance: float        # 0-1: do notes match the emotions/memory frame?
    coherence: float        # 0-1: do top/heart/base notes work together?
    safety: float           # 0-1: are all safety rules respected?
    consistency: float      # 0-1: does the story match the blueprint?
    experiential: float     # 0-1: is framing experiential not medical?
    overall: float          # weighted average

    def passed(self, threshold: float = 0.7) -> bool:
        return self.overall >= threshold


def score_relevance(intent: dict, blueprint: dict) -> float:
    """
    Checks if selected notes map to the user's emotions.
    Higher score = more notes match the emotion signals.
    """
    emotions = set(intent.get("emotions", []))
    if not emotions:
        return 0.5  # neutral if no emotions provided

    all_notes = (
        [n["family"] for n in blueprint.get("top_notes", [])] +
        [n["family"] for n in blueprint.get("heart_notes", [])] +
        [n["family"] for n in blueprint.get("base_notes", [])]
    )

    # Emotion → expected family mappings
    emotion_family_map = {
        "nostalgia": ["floral", "oriental", "woody"],
        "love": ["floral", "oriental"],
        "peace": ["aromatic", "woody", "floral"],
        "joy": ["citrus", "floral"],
        "comfort": ["oriental", "woody"],
        "excitement": ["spicy", "citrus"],
        "confident": ["woody", "spicy"],
        "calm": ["aromatic", "woody"],
        "energized": ["citrus", "spicy"],
        "elegant": ["floral", "woody"],
        "powerful": ["woody", "oriental"],
        "radiant": ["citrus", "floral"],
        "empowered": ["woody", "spicy"],
        "grounded": ["woody", "oriental"],
    }

    expected_families = set()
    for emotion in emotions:
        expected_families.update(emotion_family_map.get(emotion, []))

    if not expected_families:
        return 0.5

    matched = sum(1 for f in all_notes if f in expected_families)
    return min(matched / len(all_notes), 1.0) if all_notes else 0.0


def score_coherence(blueprint: dict) -> float:
    """
    Checks if all three layers are present and non-empty.
    Penalizes missing layers.
    """
    top = blueprint.get("top_notes", [])
    heart = blueprint.get("heart_notes", [])
    base = blueprint.get("base_notes", [])

    score = 0.0
    if top:
        score += 0.33
    if heart:
        score += 0.34
    if base:
        score += 0.33

    return round(score, 2)


def score_safety(blueprint: dict) -> float:
    """
    Checks safety compliance — safety note present,
    no banned ingredients detected.
    """
    BANNED = ["oakmoss", "peru balsam", "nitromusks", "dihydrocoumarin"]

    all_note_names = (
        [n["name"].lower() for n in blueprint.get("top_notes", [])] +
        [n["name"].lower() for n in blueprint.get("heart_notes", [])] +
        [n["name"].lower() for n in blueprint.get("base_notes", [])]
    )

    # Check banned ingredients
    for note in all_note_names:
        if note in BANNED:
            return 0.0

    # Check safety note exists
    if not blueprint.get("safety_note"):
        return 0.5

    return 1.0


def score_consistency(blueprint: dict, fragrance_story: str) -> float:
    """
    Checks if the fragrance story mentions at least some
    of the selected notes — ensures LLM didn't hallucinate.
    """
    all_note_names = (
        [n["name"].lower() for n in blueprint.get("top_notes", [])] +
        [n["name"].lower() for n in blueprint.get("heart_notes", [])] +
        [n["name"].lower() for n in blueprint.get("base_notes", [])]
    )

    if not all_note_names or not fragrance_story:
        return 0.0

    story_lower = fragrance_story.lower()
    matched = sum(1 for note in all_note_names if note in story_lower)
    return round(matched / len(all_note_names), 2)


def score_experiential(fragrance_story: str) -> float:
    """
    Checks that the story uses experiential language
    and avoids medical/therapeutic claims.
    """
    EXPERIENTIAL_TERMS = [
        "evokes", "feels like", "captures", "conjures",
        "reminds", "inspires", "suggests", "embodies",
        "brings to mind", "creates a sense of"
    ]
    BANNED_MEDICAL = [
        "treats", "heals", "cures", "therapy", "therapeutic",
        "clinical", "proven to", "reduces anxiety", "antidepressant"
    ]

    story_lower = fragrance_story.lower()

    # Fail if medical terms present
    for term in BANNED_MEDICAL:
        if term in story_lower:
            return 0.0

    # Score based on experiential terms
    found = sum(1 for term in EXPERIENTIAL_TERMS if term in story_lower)
    return min(found / 2, 1.0)   # need at least 2 experiential terms for full score


def evaluate(
    intent: dict,
    blueprint: dict,
    fragrance_story: str,
) -> RubricScore:
    """
    Runs all rubric checks and returns a RubricScore.
    Weights: relevance 30%, coherence 20%, safety 25%, consistency 15%, experiential 10%
    """
    relevance = score_relevance(intent, blueprint)
    coherence = score_coherence(blueprint)
    safety = score_safety(blueprint)
    consistency = score_consistency(blueprint, fragrance_story)
    experiential = score_experiential(fragrance_story)

    overall = (
        relevance * 0.30 +
        coherence * 0.20 +
        safety * 0.25 +
        consistency * 0.15 +
        experiential * 0.10
    )

    return RubricScore(
        relevance=relevance,
        coherence=coherence,
        safety=safety,
        consistency=consistency,
        experiential=experiential,
        overall=round(overall, 3),
    )
