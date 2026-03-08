from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class MemoryFrame(str, Enum):
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"


# --- PAST enums ---
class PastEmotion(str, Enum):
    COMFORT = "comfort"
    JOY = "joy"
    NOSTALGIA = "nostalgia"
    PEACE = "peace"
    LOVE = "love"
    EXCITEMENT = "excitement"

class AirTexture(str, Enum):
    WARM = "warm"
    FRESH = "fresh"
    HUMID = "humid"
    DRY = "dry"

class ScentHint(str, Enum):
    FLORAL = "floral"
    SWEET = "sweet"
    GREEN = "green"
    EARTHY = "earthy"
    CLEAN = "clean"
    UNCLEAR = "unclear"

class IntensityMemory(str, Enum):
    SOFT = "soft"
    GENTLE = "gentle"
    RICH = "rich"


# --- PRESENT enums ---
class LifeChapter(str, Enum):
    FAST_PACED = "fast_paced"
    BALANCED = "balanced"
    EXPLORATIVE = "explorative"
    GROUNDED = "grounded"
    TRANSFORMATIVE = "transformative"

class DailyFeeling(str, Enum):
    CONFIDENT = "confident"
    CALM = "calm"
    ENERGIZED = "energized"
    ELEGANT = "elegant"
    POWERFUL = "powerful"

class ScentDirection(str, Enum):
    FRESH_CITRUS = "fresh_citrus"
    WOODY = "woody"
    FLORAL = "floral"
    MUSKY = "musky"
    WARM_SPICY = "warm_spicy"

class SocialContext(str, Enum):
    WORK = "work"
    EVERYDAY = "everyday"
    EVENING = "evening"


# --- FUTURE enums ---
class FutureMoment(str, Enum):
    WEDDING = "wedding"
    CAREER_MILESTONE = "career_milestone"
    TRAVEL = "travel"
    PERSONAL_TRANSFORMATION = "personal_transformation"
    NEW_CHAPTER = "new_chapter"

class EmotionalIntention(str, Enum):
    RADIANT = "radiant"
    EMPOWERED = "empowered"
    EMOTIONAL = "emotional"
    GROUNDED = "grounded"
    CONFIDENT = "confident"

class DesiredImpression(str, Enum):
    MEMORABLE = "memorable"
    INTIMATE = "intimate"
    ELEGANT = "elegant"
    BOLD = "bold"
    TIMELESS = "timeless"

class ScentImagination(str, Enum):
    SOFT_FLORAL = "soft_floral"
    FRESH_LUMINOUS = "fresh_luminous"
    WARM_COMFORTING = "warm_comforting"
    DEEP_WOODY = "deep_woody"


# --- Shared ---
class SkinSensitivity(str, Enum):
    VERY_GENTLE = "very_gentle"
    BALANCED = "balanced"
    EXPRESSIVE = "expressive"

class Projection(str, Enum):
    SKIN_CLOSE = "skin_close"
    BALANCED = "balanced"
    STATEMENT = "statement"

class Longevity(str, Enum):
    SUBTLE = "subtle"
    EVOLVING = "evolving"
    LASTING = "lasting"


# --- Past questionnaire payload ---
class PastQuestionnaire(BaseModel):
    memory_description: str = Field(..., description="Free text description of the memory")
    emotions: list[PastEmotion]
    air_texture: AirTexture
    scent_hints: list[ScentHint]
    intensity_memory: IntensityMemory
    skin_sensitivity: SkinSensitivity


# --- Present questionnaire payload ---
class PresentQuestionnaire(BaseModel):
    life_chapter: LifeChapter
    daily_feeling: list[DailyFeeling]
    scent_direction: ScentDirection
    social_context: SocialContext
    projection: Projection


# --- Future questionnaire payload ---
class FutureQuestionnaire(BaseModel):
    future_moment: FutureMoment
    emotional_intention: list[EmotionalIntention]
    desired_impression: list[DesiredImpression]
    scent_imagination: ScentImagination
    longevity: Longevity


# --- Master Scent Intent JSON ---
class ScentIntentJSON(BaseModel):
    memory_frame: MemoryFrame
    past: Optional[PastQuestionnaire] = None
    present: Optional[PresentQuestionnaire] = None
    future: Optional[FutureQuestionnaire] = None
    free_text_memory: Optional[str] = Field(None, description="Optional free text from user")

    # Extracted signals (populated by signal_extraction.py)
    emotions: list[str] = Field(default_factory=list)
    imagery: list[str] = Field(default_factory=list)
    desired_intensity: Optional[str] = None
    environmental_context: Optional[str] = None
    skin_sensitivity_constraint: Optional[SkinSensitivity] = None
