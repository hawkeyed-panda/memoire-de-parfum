from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from app.auth.jwt import create_access_token
from app.errors.exceptions import InvalidTokenError

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


@router.post("/token", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login endpoint — returns JWT access token.
    In production: verify against Postgres user table.
    For demo: accepts any valid email/password.
    """
    # TODO: replace with real DB lookup
    # user = await get_user_by_email(db, request.email)
    # if not user or not verify_password(request.password, user.hashed_password):
    #     raise InvalidTokenError()

    token = create_access_token(data={"sub": request.email})
    return TokenResponse(access_token=token)
