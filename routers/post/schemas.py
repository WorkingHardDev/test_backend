from pydantic import BaseModel


class PostSchema(BaseModel):
    text: str
    user_id: int
