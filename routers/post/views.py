import asyncio

from cachetools import TTLCache
from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.requests import Request

from core.utils import async_cached
from db.models.post import PostStore

from routers.post.schemas import PostSchema

cache = TTLCache(maxsize=100, ttl=300)
router = APIRouter(
    prefix="/posts",
    tags=["Post"],
)


async def check_payload_size(request: Request):
    body = await request.body()
    size_in_mb = len(body) / (1024 * 1024)
    if size_in_mb > 1:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail="Payload too large. Size should not exceed 1 MB.")


@router.post(
    "",
    response_model=PostSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_payload_size)]
)
async def create_post(
        post_income: PostSchema,
):
    post = post_income.model_dump()
    post = await PostStore.create_post(data=post)
    cache.clear()
    return post


@router.get(
    "",
    response_model=list[PostSchema],
    status_code=status.HTTP_200_OK,
)
@async_cached(cache=cache)
async def get_posts():
    post = await PostStore.get_all_posts()
    await asyncio.sleep(1)
    return post


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(post_id: int):
    cache.clear()
    return await PostStore.delete_post(post_id=post_id)
