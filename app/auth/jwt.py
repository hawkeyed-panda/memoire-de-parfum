from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.config import settings
from app.errors.exceptions import InvalidTokenError


def create_access_token(data: dict) -> str:
    """
    Creates a signed JWT access token.
    Adds expiry time before signing.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def verify_access_token(token: str) -> dict:
    """
    Verifies and decodes a JWT token.
    Raises InvalidTokenError if token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise InvalidTokenError()
        return payload

    except JWTError:
        raise InvalidTokenError()