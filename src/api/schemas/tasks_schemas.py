from typing import Literal
from pydantic import BaseModel, Field

from src.db.models import AllowedTaskStatus


class CreateTaskSchema(BaseModel):
    title: str
    description: str
    assignee_id: int

class TaskInfoSchema(BaseModel):
    id: int
    title: str
    description: str
    status: AllowedTaskStatus = Field(default="todo")
    assignee_id: int

class UpdateTaskSchema(BaseModel):
    title: str = Field(default="")
    description: str = Field(default="")
    status: Literal[AllowedTaskStatus, ""] = Field(default="")

