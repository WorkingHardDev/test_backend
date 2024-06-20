from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str | bytes


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
