import os

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class AuthJWT(BaseModel):
    private_key_path: str = os.getenv("JWT_SECRET_KEY", "1234")
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = 0.1
    refresh_token_expire_minutes: int = 1


class DbSettings(BaseModel):
    DB_USER: str = os.getenv("MYSQL_USER", "root")
    DB_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    DB_HOST: str = os.getenv("MYSQL_HOST", "127.0.0.1")
    DB_PORT: str = os.getenv("MYSQL_PORT", "3306")
    DB_NAME: str = os.getenv("MYSQL_DATABASE", "mysql")
    url: str = f'mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


class Settings(BaseSettings):
    db: DbSettings = DbSettings()

    auth_jwt: AuthJWT = AuthJWT()

    access_token: str = "access_token"
    refresh_token: str = "refresh_token"

    # routes which do not require authorization
    exclude_jwt_paths: set[tuple[str, str]] = {
        ("/docs", "GET"),
        ("/openapi.json", "GET"),
        ("/user", "POST"),
        ("/jwt/login", "POST"),
        ("/jwt/logout", "POST"),
    }


settings = Settings()

