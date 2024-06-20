from datetime import datetime, timedelta

from sqlalchemy import DateTime, func, select, delete, String
from sqlalchemy.orm import Mapped, mapped_column

from core.config import settings
from db.decorators.db_session import db_session
from db.mysql import Base


class Token(Base):
    access_token: Mapped[str] = mapped_column(String(255))
    refresh_token: Mapped[str] = mapped_column(String(255))
    created_at = mapped_column(DateTime, default=func.now())


class TokenStore:
    '''
    Store class for DB calls to tokens table
    '''
    @staticmethod
    @db_session
    async def create(session, data: dict):
        token = Token(**data)
        session.add(token)
        await session.commit()
        return token

    @staticmethod
    @db_session
    async def update_access_token(session, refresh_token: str, data):
        token = await session.execute(select(Token).where(Token.refresh_token == refresh_token))
        token = token.scalar_one_or_none()
        if token:
            token.access_token = data
            await session.commit()
            return token
        return None

    @staticmethod
    @db_session
    async def delete_by_refresh_token(session, refresh_token: str):
        expire_time = datetime.now() + timedelta(minutes=settings.auth_jwt.refresh_token_expire_minutes)
        try:
            # Delete specific token that is expired based on the refresh_token settings
            delete_specific_token_query = delete(Token).where(Token.refresh_token == refresh_token)
            await session.execute(delete_specific_token_query)

            # Delete all tokens that were created more than 30 days ago
            delete_expired_tokens_query = delete(Token).where(
                Token.created_at < expire_time
            )
            await session.execute(delete_expired_tokens_query)

            # Commit the transaction if any of the above operations made changes
            await session.commit()
        except Exception as e:
            # Rollback in case of any exception during the transaction
            await session.rollback()
            raise e

    @staticmethod
    @db_session
    async def delete_old_tokens(session):
        expire_duration = timedelta(minutes=settings.auth_jwt.refresh_token_expire_minutes)
        await session.execute(delete(Token).where(Token.created_at > datetime.now() + expire_duration))
        await session.commit()
        return None
