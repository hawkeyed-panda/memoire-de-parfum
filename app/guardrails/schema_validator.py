from app.models.blueprint import FragranceBlueprintJSON
from app.errors.exceptions import SchemaValidationError


def validate_blueprint_schema(blueprint: FragranceBlueprintJSON) -> None:
    """
    Inline guardrail — ensures every blueprint has required fields
    before it reaches LLM synthesis.
    """
    if not blueprint.top_notes:
        raise SchemaValidationError("Blueprint missing top notes")

    if not blueprint.heart_notes:
        raise SchemaValidationError("Blueprint missing heart notes")

    if not blueprint.base_notes:
        raise SchemaValidationError("Blueprint missing base notes")

    if not blueprint.safety_note:
        raise SchemaValidationError("Blueprint missing safety note")

    if not blueprint.intensity:
        raise SchemaValidationError("Blueprint missing intensity guidance")
