from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

AllowedRoles = Literal["owner", "member"]

class ProjectSchema(BaseModel):
    name: str = Field(title="Название проекта",
                      description="Название должно быть от 5 до 25 символов",
                      min_length=5,
                      max_length=25,
                      examples=["Microsoft API project"])

class ProjectSchemaWithId(ProjectSchema):
    id: int = Field(title="Айди проекта",
                    description="Должно быть больше 0 и меньше 2147483647",
                    gt=0,
                    lt=2147483647)

class ProjectResponseSchema(ProjectSchemaWithId):
    """Схема для ответов. Возвращает айди проекта и его название"""
    pass

class CreateProjectSchema(ProjectSchema):
    """Схема для создания нового проекта. Принимает только название"""
    pass

class UpdateProjectSchema(ProjectSchema):
    """Схема для обновления названия проекта. Требуется только его название"""
    pass

class ProjectMemberSchema(BaseModel):
    """Схема для валидации участников проекта. Нигде в ручках напрямую не используется, но требуется в качестве списка для ProjectInfoSchema"""
    user_id: int = Field(default=0, lt=2147483647)
    role: AllowedRoles = Field(title="Роль пользователя",
                               description="Принимаются только два значения - owner и member",
                               examples=["owner", "member"])

    model_config = ConfigDict(from_attributes=True)

class ProjectInfoSchema(ProjectSchemaWithId):
    members: list[ProjectMemberSchema] = Field(title="Участники проекта",
                                               description="Список всех участников с их айди и ролью")

    model_config = ConfigDict(from_attributes=True)

class ProjectMemberIdSchema(BaseModel):
    user_id: int = Field(title="Айди участника проекта",
                         default=0,
                         lt=2147483647)

    model_config = ConfigDict(from_attributes=True)