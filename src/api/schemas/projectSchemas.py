from pydantic import BaseModel, ConfigDict


class CreateProjectSchema(BaseModel):
    name: str


class ProjectMemberSchema(BaseModel):
    user_id: int
    role: str

    model_config = ConfigDict(from_attributes=True)

class ProjectInfoSchema(BaseModel):
    id: int
    name: str
    members: list[ProjectMemberSchema]

    model_config = ConfigDict(from_attributes=True)

class ProjectAddMemberSchema(BaseModel):
    user_id: int

    model_config = ConfigDict(from_attributes=True)