from pydantic import BaseModel, Field


class CreateCommentSchema(BaseModel):
    text: str

class CommentInfoSchema(BaseModel):
    id: int
    author_id: int
    text: str

class CommentUpdateSchema(BaseModel):
    text: str = Field(min_length=1, default="")