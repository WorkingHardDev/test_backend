import datetime
from core.config import settings
from db.models.user import UserStore
from jwt.exceptions import InvalidTokenError
from routers.user.schemas import TokenSchema, UserSchema
from fastapi import (
    HTTPException,
    status,
    Request,
    Response
)
from auth import utils as auth_utils
from db.models.token import TokenStore


async def validate_auth_user(
        email: str,
        password: str,
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid email or password",
    )

    user: UserSchema = await UserStore.get_user_by_email(email=email)

    if not user:
        raise unauthed_exc

    if not auth_utils.validate_password(
            password=password,
            hashed_password=user.password,
    ):
        raise unauthed_exc

    return user


async def get_current_token_payload(
        request: Request,
        response: Response
) -> dict:
    try:
        token: str = request.cookies.get(settings.access_token, None)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"You are not authorized",
            )
        payload: dict = auth_utils.decode_jwt(
            token=token,
        )

    except InvalidTokenError as e:
        if str(e) == "Signature has expired":
            return await auth_utils.refreshing_token(response, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {e}",
        )

    return payload


async def refresh_jwt_token(token: str):
    try:
        payload: dict = auth_utils.decode_jwt(token)
        user = await UserStore.get_user_by_id(user_id=payload["sub"])
        access_payload = {
            "sub": user.id,
            "email": user.email,
        }
        access_token: str | bytes = auth_utils.encode_jwt(access_payload)
        await TokenStore.update_access_token(refresh_token=token, data=access_token)
        return access_token
    except InvalidTokenError as e:
        await TokenStore.delete_by_refresh_token(refresh_token=token)
        return None


async def generate_tokens_and_set_cookies(user, response):
    '''
    Generates JWT tokens and sets them to cookies
    '''
    access_payload = {
        "sub": user.id,
        "email": user.email,
    }
    access_token = auth_utils.encode_jwt(access_payload)

    refresh_payload = {
        "sub": user.id,
        "email": user.email,
        "type": "refresh",
    }
    refresh_token = auth_utils.encode_jwt(refresh_payload,
                                          expire_timedelta=datetime.timedelta(
                                              minutes=settings.auth_jwt.refresh_token_expire_minutes))

    token = {"access_token": access_token, "refresh_token": refresh_token}

    await TokenStore.create(data=token)
    response.set_cookie(settings.access_token, access_token, samesite='none', secure=True, httponly=True)
    response.set_cookie(settings.refresh_token, refresh_token, samesite='none', httponly=True, secure=True)

    token_schema = TokenSchema(access_token=access_token,
                               refresh_token=refresh_token, )

    return token_schema
