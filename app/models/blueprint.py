from pydantic import BaseModel, Field
from typing import Optional
from app.models.intent import MemoryFrame, SkinSensitivity


class FragranceNote(BaseModel):
    name: str
    family: str                          # e.g. floral, woody, citrus
    description: str                     # what it evokes
    is_substituted: bool = False         # True if original note was swapped for safety
    substituted_from: Optional[str] = None


class FragranceBlueprintJSON(BaseModel):
    memory_frame: MemoryFrame

    # Core composition
    top_notes: list[FragranceNote]       # first impression, 0–30 min
    heart_notes: list[FragranceNote]     # core character, 30 min–3 hrs
    base_notes: list[FragranceNote]      # lasting impression, 3+ hrs

    # Guidance
    intensity: str                       # soft / moderate / rich
    projection: str                      # skin-close / balanced / statement
    longevity: str                       # subtle / evolving / lasting

    # Safety
    skin_sensitivity: SkinSensitivity
    safety_note: str                     # always required — guardrail enforces this
    substitutions_applied: list[str] = Field(default_factory=list)

    # Grounding references (populated by doc_rag.py)
    retrieved_references: list[str] = Field(default_factory=list)

    # Meta
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    memory_frame_explanation: Optional[str] = None  # why these notes fit this frame