import datetime
import logging
import jwt
from fastapi import Request, status, HTTPException, Response
from auth import utils as auth_utils

from core.config import settings
from fastapi.responses import JSONResponse

from db.models.user import UserStore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def auth_middleware(request: Request, response: Response, call_next):
    '''
    Middleware function for auth middleware. That check and push JWT token to request
    '''
    if request.method == "OPTIONS" or (
            request.url.path, request.method) in settings.exclude_jwt_paths:
        response = await call_next(request)
        return response

    payload = None
    token: str = request.cookies.get(settings.access_token, None)
    if not token:
        return JSONResponse(status_code=401, content={"detail": "You are not authorized"})
    try:
        payload = auth_utils.decode_jwt(token=token)

    except jwt.ExpiredSignatureError:
        try:
            token = await auth_utils.refreshing_token(response, request)
            payload = auth_utils.decode_jwt(token=token)
        except HTTPException as e:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={"detail": "Token expired and refresh failed"})

    except jwt.InvalidTokenError as e:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": f"Invalid token error: {e}"},
        )
    try:
        request.state.payload = payload
        logging.info('access')
        user = await UserStore.get_user_by_id(user_id=payload['sub'])

        if user is None:
            # User not found, handle accordingly
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "User not found"})

        response = await call_next(request)
        return response

    except HTTPException as http_exception:

        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(http_exception)})
