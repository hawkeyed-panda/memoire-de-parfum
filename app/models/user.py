from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from app.models.blueprint import FragranceBlueprintJSON
from app.models.intent import ScentIntentJSON


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime


class SavedBlend(BaseModel):
    id: str
    user_id: str
    name: Optional[str] = Field(None, description="User-given name for this blend")
    intent: ScentIntentJSON
    blueprint: FragranceBlueprintJSON
    version: int = 1                     # increments on each refine
    created_at: datetime
    updated_at: datetime


class SessionData(BaseModel):
    user_id: str
    current_intent: Optional[ScentIntentJSON] = None
    current_blueprint: Optional[FragranceBlueprintJSON] = None
    refinement_count: int = 0