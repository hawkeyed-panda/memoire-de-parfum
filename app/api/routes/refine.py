from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Literal
from app.models.intent import ScentIntentJSON
from app.pipeline.fragrance_pipeline import run_refinement_pipeline
from app.auth.rate_limit import check_rate_limit
from app.api.deps import get_optional_user

router = APIRouter(prefix="/refine", tags=["refine"])


class RefinementRequest(BaseModel):
    intent: ScentIntentJSON
    refinement: Literal["lighter", "stronger", "warmer", "fresher"]


@router.post("/")
async def refine_fragrance(
    request: Request,
    body: RefinementRequest,
    user: dict = Depends(get_optional_user),
):
    """
    Refines an existing fragrance blueprint.
    Accepts: lighter, stronger, warmer, fresher.
    Re-runs from GraphRAG onwards — skips signal extraction.
    """
    await check_rate_limit(request)

    result = await run_refinement_pipeline(
        existing_intent=body.intent,
        refinement=body.refinement,
    )

    return result
