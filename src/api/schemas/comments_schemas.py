from pydantic import BaseModel

class CreateCommentSchema(BaseModel):
    text: str