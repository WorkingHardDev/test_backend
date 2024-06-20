from auth.jwt_helper import validate_auth_user, generate_tokens_and_set_cookies
from core.config import settings
from db.models.token import TokenStore
from routers.jwt_auth.schemas import LoginCredentialsSchema
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Response,
    Request,
)
from routers.user.schemas import TokenSchema

router = APIRouter(prefix="/jwt", tags=["JWT"])


@router.post("/login", response_model=TokenSchema)
async def auth_user_issue_jwt(
        response: Response,
        credentials: LoginCredentialsSchema,
):
    email = credentials.email
    password = credentials.password
    user = await validate_auth_user(email, password)
    return await generate_tokens_and_set_cookies(user, response)


@router.get("/logout")
async def demo_auth_logout_cookie(
        response: Response,
        request: Request
) -> dict:
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authenticated",
        )
    response.delete_cookie(settings.access_token)
    response.delete_cookie(settings.refresh_token)
    await TokenStore.delete_by_refresh_token(refresh_token=token)
    return {
        "message": f"Bye!",
    }
