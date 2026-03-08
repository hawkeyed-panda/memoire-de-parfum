from fastapi import APIRouter, Depends, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from app.models.intent import MemoryFrame, PastQuestionnaire, PresentQuestionnaire, FutureQuestionnaire
from app.pipeline.fragrance_pipeline import run_fragrance_pipeline
from app.auth.rate_limit import check_rate_limit
from app.api.deps import get_optional_user

router = APIRouter(prefix="/fragrance", tags=["fragrance"])


class FragranceRequest(BaseModel):
    memory_frame: MemoryFrame
    past: Optional[PastQuestionnaire] = None
    present: Optional[PresentQuestionnaire] = None
    future: Optional[FutureQuestionnaire] = None
    free_text_memory: Optional[str] = None


@router.post("/generate")
async def generate_fragrance(
    request: Request,
    body: FragranceRequest,
    user: dict = Depends(get_optional_user),
):
    """
    Runs the full fragrance pipeline.
    Returns blueprint + fragrance story.
    """
    await check_rate_limit(request)

    questionnaire_data = {}
    if body.memory_frame == MemoryFrame.PAST and body.past:
        questionnaire_data = body.past.model_dump()
    elif body.memory_frame == MemoryFrame.PRESENT and body.present:
        questionnaire_data = body.present.model_dump()
    elif body.memory_frame == MemoryFrame.FUTURE and body.future:
        questionnaire_data = body.future.model_dump()

    result = await run_fragrance_pipeline(
        memory_frame=body.memory_frame,
        questionnaire_data=questionnaire_data,
        free_text_memory=body.free_text_memory or "",
    )

    return result
