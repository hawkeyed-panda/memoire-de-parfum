from app.errors.exceptions import PolicyRuleViolation


# Words that imply medical or therapeutic effects — not allowed
BANNED_MEDICAL_TERMS = [
    "treats", "heals", "cures", "therapy", "therapeutic",
    "medical", "clinical", "diagnose", "remedy", "relieves pain",
    "anti-inflammatory", "antidepressant", "sedative", "antibacterial",
    "antiseptic", "proven to", "scientifically proven", "reduces anxiety",
    "cures depression", "treats insomnia",
]

# Words we want instead — experiential framing
ALLOWED_EXPERIENTIAL_TERMS = [
    "evokes", "feels like", "reminds", "captures",
    "suggests", "inspires", "creates a sense of",
    "brings to mind", "conjures", "embodies"
]


def apply_policy_rules(output_text: str) -> None:
    """
    Inline guardrail — runs inside llm_synthesis after text is generated.
    Blocks any medical or therapeutic claims in the final output.
    Raises PolicyRuleViolation if banned terms are found.
    """
    output_lower = output_text.lower()

    violations = [
        term for term in BANNED_MEDICAL_TERMS
        if term in output_lower
    ]

    if violations:
        raise PolicyRuleViolation(
            message=f"Output contains disallowed medical claims: {', '.join(violations)}"
        )


def check_experiential_framing(output_text: str) -> bool:
    """
    Soft check — returns True if output uses at least one
    experiential framing term. Used as a quality signal, not hard block.
    """
    output_lower = output_text.lower()
    return any(term in output_lower for term in ALLOWED_EXPERIENTIAL_TERMS)
