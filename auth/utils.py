from datetime import datetime, timedelta
import bcrypt
import jwt


from core.config import settings
from fastapi import Response, Request, HTTPException, status


def encode_jwt(
        payload: dict,
        private_key: str = settings.auth_jwt.private_key_path,
        algorithm: str = settings.auth_jwt.algorithm,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
        token: str | bytes,
        public_key: str = settings.auth_jwt.private_key_path,
        algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


def hash_password(
        password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
        password: str,
        hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


async def refreshing_token(response: Response, request: Request):
    from auth.jwt_helper import refresh_jwt_token
    refresh_token = request.cookies.get(settings.refresh_token, None)
    if refresh_token:
        access_token = await refresh_jwt_token(token=refresh_token)
        if access_token:
            response.set_cookie(settings.access_token, access_token, httponly=True, samesite='none', secure=True)
            return access_token
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is expired')