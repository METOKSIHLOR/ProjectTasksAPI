from pydantic import BaseModel, ConfigDict, Field


class ProjectSchema(BaseModel):
    name: str = Field(default="", min_length=5, max_length=22)

class ProjectDeleteSchema(BaseModel):
    id: int = Field(default=0, lt=2147483647)

class ProjectMemberSchema(BaseModel):
    user_id: int = Field(default=0, lt=2147483647)
    role: str

    model_config = ConfigDict(from_attributes=True)

class ProjectInfoSchema(BaseModel):
    id: int
    name: str
    members: list[ProjectMemberSchema]

    model_config = ConfigDict(from_attributes=True)

class ProjectMemberIdSchema(BaseModel):
    user_id: int =  Field(default=0, lt=2147483647)

    model_config = ConfigDict(from_attributes=True)