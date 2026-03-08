from app.models.blueprint import FragranceBlueprintJSON
from app.models.intent import SkinSensitivity
from app.errors.exceptions import SafetyRuleViolation


ABSOLUTE_BANNED = [
    "oakmoss", "peru balsam", "nitromusks",
    "dihydrocoumarin", "methyl eugenol"
]


def apply_safety_rules(
    blueprint: FragranceBlueprintJSON,
    sensitivity: SkinSensitivity
) -> None:
    """
    Inline guardrail — runs inside constraint_selector.
    Raises SafetyRuleViolation if any banned ingredient is present.
    """
    all_notes = (
        blueprint.top_notes +
        blueprint.heart_notes +
        blueprint.base_notes
    )

    for note in all_notes:
        if note.name.lower() in ABSOLUTE_BANNED:
            raise SafetyRuleViolation(
                message=f"Banned ingredient detected: {note.name}"
            )

    # Sensitive skin extra check
    if sensitivity == SkinSensitivity.VERY_GENTLE:
        gentle_avoid = ["ylang ylang", "cinnamon", "clove", "lemongrass"]
        for note in all_notes:
            if note.name.lower() in gentle_avoid:
                raise SafetyRuleViolation(
                    message=f"{note.name} is not safe for very gentle/sensitive skin"
                )
