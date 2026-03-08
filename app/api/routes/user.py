from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
from app.models.intent import ScentIntentJSON
from app.models.blueprint import FragranceBlueprintJSON
from app.api.deps import get_current_user
from app.auth.rate_limit import check_rate_limit

router = APIRouter(prefix="/user", tags=["user"])

# In-memory store for demo — replace with Postgres in production
_saved_blends: dict = {}


class SaveBlendRequest(BaseModel):
    name: Optional[str] = None
    intent: ScentIntentJSON
    blueprint: FragranceBlueprintJSON
    fragrance_story: str


class SavedBlendResponse(BaseModel):
    id: str
    name: Optional[str]
    created_at: datetime
    fragrance_story: str


@router.post("/blends/save", response_model=SavedBlendResponse)
async def save_blend(
    request: Request,
    body: SaveBlendRequest,
    user: dict = Depends(get_current_user),
):
    """Save a fragrance blend to the user's profile."""
    await check_rate_limit(request)

    blend_id = str(uuid.uuid4())
    user_id = user.get("sub")
    created_at = datetime.utcnow()

    _saved_blends[blend_id] = {
        "id": blend_id,
        "user_id": user_id,
        "name": body.name or f"Blend {created_at.strftime('%b %d')}",
        "intent": body.intent.model_dump(),
        "blueprint": body.blueprint.model_dump(),
        "fragrance_story": body.fragrance_story,
        "created_at": created_at,
        "version": 1,
    }

    return SavedBlendResponse(
        id=blend_id,
        name=_saved_blends[blend_id]["name"],
        created_at=created_at,
        fragrance_story=body.fragrance_story,
    )


@router.get("/blends")
async def get_blends(
    user: dict = Depends(get_current_user),
):
    """Get all saved blends for the current user."""
    user_id = user.get("sub")
    user_blends = [
        b for b in _saved_blends.values()
        if b["user_id"] == user_id
    ]
    return user_blends
