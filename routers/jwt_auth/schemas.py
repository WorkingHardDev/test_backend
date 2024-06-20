from pydantic import BaseModel, EmailStr


class LoginCredentialsSchema(BaseModel):
    email: EmailStr
    password: str