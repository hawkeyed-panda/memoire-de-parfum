from typing import Optional

from fastapi import Depends, Header
from app.auth.jwt import verify_access_token
from app.errors.exceptions import InvalidTokenError


async def get_current_user(
    authorization: str = Header(..., description="Bearer <token>")
) -> dict:
    """
    FastAPI dependency — extracts and verifies JWT from Authorization header.
    Inject into any protected route.
    """
    if not authorization.startswith("Bearer "):
        raise InvalidTokenError()

    token = authorization.split(" ")[1]
    payload = verify_access_token(token)
    return payload


async def get_optional_user(
    authorization: str = Header(None)
) -> Optional[dict]:
    """
    Optional auth dependency — returns None if no token provided.
    Used for routes that work both authenticated and unauthenticated.
    """
    if not authorization:
        return None
    try:
        return await get_current_user(authorization)
    except Exception:
        return None