from app.models.blueprint import FragranceBlueprintJSON
from app.errors.exceptions import GroundingRuleViolation


# Minimum number of retrieved references required to ground the output
MIN_REFERENCES_REQUIRED = 1


def apply_grounding_rules(
    blueprint: FragranceBlueprintJSON,
    retrieved_references: list[str]
) -> None:
    """
    Inline guardrail — runs inside llm_synthesis.
    Ensures the output is grounded in retrieved graph facts or doc snippets.
    Raises GroundingRuleViolation if not enough references exist.
    """
    if not retrieved_references or len(retrieved_references) < MIN_REFERENCES_REQUIRED:
        raise GroundingRuleViolation(
            message="Output must be supported by at least one retrieved reference"
        )

    # Ensure at least one selected note is mentioned in the references
    all_note_names = (
        [n.name.lower() for n in blueprint.top_notes] +
        [n.name.lower() for n in blueprint.heart_notes] +
        [n.name.lower() for n in blueprint.base_notes]
    )

    references_text = " ".join(retrieved_references).lower()
    matched = [note for note in all_note_names if note in references_text]

    if not matched:
        raise GroundingRuleViolation(
            message="None of the selected notes are mentioned in retrieved references"
        )
