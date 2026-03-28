from pydantic import BaseModel, ConfigDict, Field


class ProjectSchema(BaseModel):
    name: str = Field(default="", min_length=5)


class ProjectMemberSchema(BaseModel):
    user_id: int = Field(..., lt=2147483647)
    role: str

    model_config = ConfigDict(from_attributes=True)

class ProjectInfoSchema(BaseModel):
    id: int
    name: str
    members: list[ProjectMemberSchema]

    model_config = ConfigDict(from_attributes=True)

class ProjectAddMemberSchema(BaseModel):
    user_id: int =  Field(..., lt=2147483647)

    model_config = ConfigDict(from_attributes=True)