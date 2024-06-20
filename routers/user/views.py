from fastapi import APIRouter, BackgroundTasks, Response
from fastapi.responses import JSONResponse
from starlette import status

from db.models.user import UserStore
from routers.user.schemas import UserSchema

router = APIRouter(
    prefix="/users",
    tags=["User"],
)


@router.post(
    "",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_income: UserSchema,
):
    user = user_income.model_dump()
    user = await UserStore.create_user(data=user)
    return user
