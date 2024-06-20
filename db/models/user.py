from fastapi import HTTPException
from sqlalchemy import select, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column, relationship
from starlette import status
from auth import utils as auth_utils
from db.decorators.db_session import db_session
from db.mysql import Base
from routers.user.schemas import UserSchema
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.models.post import Post


class User(Base):
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    password: Mapped[bytes] = mapped_column()
    email: Mapped[str] = mapped_column(String(255), unique=True)
    posts = relationship("Post", back_populates="user")


class UserStore:
    '''
    Store class for DB calls to users table
    '''
    @staticmethod
    @db_session
    async def create_user(session, data: UserSchema) -> User:
        try:
            data["password"] = auth_utils.hash_password(data["password"])
            user = User(**data)
            session.add(user)
            await session.commit()
            if user:
                return user
        except IntegrityError as e:
            await session.rollback()
            # Inspecting the exception to check for a unique constraint
            if "Duplicate entry" in str(e):
                # Determine which field caused the unique constraint error
                if 'users.username' in str(e):
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
                elif 'users.email' in str(e):
                    print(34256787)
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
                else:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                        detail="A unique constraint error occurred, please check your data.")
            else:
                # If the error is not due to a unique constraint, re-raise it
                raise e

    @staticmethod
    @db_session
    async def get_user_by_email(session, email: str):
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        return user

    @staticmethod
    @db_session
    async def get_user_by_id(session, user_id: int) -> UserSchema:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        return user
