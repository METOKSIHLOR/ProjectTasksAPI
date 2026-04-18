from uuid import UUID
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

AllowedRoles = Literal["owner", "member"]

class ProjectSchema(BaseModel):
    name: str = Field(title="Название проекта",
                      description="Название должно быть от 3 до 25 символов",
                      min_length=3,
                      max_length=25,
                      examples=["Microsoft API project"])

class ProjectSchemaWithId(ProjectSchema):
    id: UUID = Field(title="Айди проекта",
                    description="Должно быть uuid",)

class ProjectSchemaWithOwnerEmail(ProjectSchemaWithId):
    owner_email: EmailStr = Field(title="Почта владельца проекта",
                                  examples=["metoks@gmail.com"], )

class ProjectResponseSchema(ProjectSchemaWithId):
    """Схема для ответов. Возвращает айди проекта и его название"""
    pass

class CreateProjectSchema(ProjectSchema):
    """Схема для создания нового проекта. Принимает только название"""
    pass

class UpdateProjectSchema(ProjectSchema):
    """Схема для обновления названия проекта. Требуется только его название"""
    name: str = Field(title="Название проекта",
                      description="Название должно быть от 3 до 25 символов",
                      min_length=3,
                      max_length=25,
                      examples=[""])

class ProjectMemberSchema(BaseModel):
    """Схема для валидации участников проекта. Нигде в ручках напрямую не используется, но требуется в качестве списка для ProjectSchemaWithMembers"""
    name: str = Field(title="Имя пользователя")
    email: EmailStr = Field(title="Почта пользователя",
                            examples=["metoks@gmail.com"])
    role: AllowedRoles = Field(title="Роль пользователя",
                               description="Принимаются только два значения - owner и member",
                               examples=["owner", "member"])

    model_config = ConfigDict(from_attributes=True)

class ProjectSchemaWithMembers(ProjectSchemaWithOwnerEmail):
    members: list[ProjectMemberSchema] = Field(title="Участники проекта",
                                               description="Список всех участников с их именами, почтой и ролью")

    model_config = ConfigDict(from_attributes=True)

class ProjectMemberIdSchema(BaseModel):
    email: EmailStr = Field(title="Почта пользователя",
                            examples=["metoks@gmail.com"])

    model_config = ConfigDict(from_attributes=True)