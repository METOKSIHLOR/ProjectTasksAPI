
from pydantic import BaseModel, Field


class CreateTaskSchema(BaseModel):
    title: str
    description: str
    assignee_id: int

class TaskInfoSchema(BaseModel):
    id: int
    title: str
    description: str
    status: str = Field(default="todo")
    assignee_id: int

