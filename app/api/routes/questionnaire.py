from fastapi import APIRouter, Depends, Request
from app.models.intent import (
    MemoryFrame,
    PastQuestionnaire,
    PresentQuestionnaire,
    FutureQuestionnaire,
    ScentIntentJSON,
)
from app.core.signal_extraction import extract_scent_signals
from app.auth.rate_limit import check_rate_limit
from app.api.deps import get_optional_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/questionnaire", tags=["questionnaire"])


class QuestionnaireRequest(BaseModel):
    memory_frame: MemoryFrame
    past: Optional[PastQuestionnaire] = None
    present: Optional[PresentQuestionnaire] = None
    future: Optional[FutureQuestionnaire] = None
    free_text_memory: Optional[str] = None


@router.post("/extract", response_model=ScentIntentJSON)
async def extract_intent(
    request: Request,
    body: QuestionnaireRequest,
    user: dict = Depends(get_optional_user),
):
    """
    Extracts a ScentIntentJSON from questionnaire answers.
    Does NOT run the full pipeline — just signal extraction.
    Used by the frontend to preview extracted signals before generation.
    """
    await check_rate_limit(request)

    # Build questionnaire data dict from whichever frame was selected
    questionnaire_data = {}
    if body.memory_frame == MemoryFrame.PAST and body.past:
        questionnaire_data = body.past.model_dump()
    elif body.memory_frame == MemoryFrame.PRESENT and body.present:
        questionnaire_data = body.present.model_dump()
    elif body.memory_frame == MemoryFrame.FUTURE and body.future:
        questionnaire_data = body.future.model_dump()

    intent = await extract_scent_signals(
        memory_frame=body.memory_frame,
        questionnaire_data=questionnaire_data,
        free_text_memory=body.free_text_memory or "",
    )

    return intent
