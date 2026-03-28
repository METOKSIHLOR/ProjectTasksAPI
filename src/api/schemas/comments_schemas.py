from pydantic import BaseModel

class CreateCommentSchema(BaseModel):
    text: str

class CommentInfoSchema(BaseModel):
    id: int
    author_id: int
    text: str

    class Config:
        from_attributes = True