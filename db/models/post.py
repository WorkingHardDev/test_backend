
from sqlalchemy import ForeignKey, Integer, Text, delete, select
from sqlalchemy.orm import mapped_column, Mapped, relationship

from db.decorators.db_session import db_session
from db.mysql import Base
from routers.post.schemas import PostSchema
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.models.user import User


class Post(Base):
    text: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(Integer(), ForeignKey("users.id"))
    user = relationship("User", back_populates="posts")


class PostStore:
    '''
    Store class for DB calls to posts table
    '''
    @staticmethod
    @db_session
    async def create_post(session, data: PostSchema):
        post = Post(**data)
        session.add(post)
        await session.commit()
        return post

    @staticmethod
    @db_session
    async def get_post_by_id(session, post_id: int):
        result = await session.execute(select(Post).where(Post.id == post_id))
        post = result.scalar_one_or_none()
        return post

    @staticmethod
    @db_session
    async def get_all_posts(session) -> Post:
        result = await session.execute(select(Post))
        posts = [row[0] for row in result.all()]
        return posts



    @staticmethod
    @db_session
    async def delete_post(session, post_id: int):
        post = delete(Post).where(Post.id == post_id)
        await session.execute(post)

