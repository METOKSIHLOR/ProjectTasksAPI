from typing import Literal, List
from pydantic import Field
from pydantic import BaseModel, EmailStr

from uuid import UUID


class UserCredsSchema(BaseModel):
    """Схема с минмальными необходимым данными для авторизации пользователя, логином и паролем"""
    email: EmailStr = Field(title="Почта пользователя",
                            description="Принимается любая почта, которая содержит @",
                            examples=["metoks@gmail.com", "trap@abcde.ru"],)
    
    password: str = Field(min_length=5,
                          title="Пароль пользователя",
                          description="Пароль должен быть >= 5 символов",
                          examples=["abcdef", "qwerty229"])

class UserRegistrationSchema(UserCredsSchema):
    """Схема с данными пользователя для регистрации. Имя аккаунта, почта и пароль. Идентификация юзера проиходит по почте"""
    name: str = Field(min_length=3, title="Имя пользователя",
                      description="Не меньше 3 символов",
                      examples=["METOKS", "Antooooooon"])

class UpdateUserSchema(BaseModel):
    """Схема для обновления имени пользователя"""
    name: str | None = Field(None, min_length=3, title="Имя пользователя",
                      description="Не меньше 3 символов",
                      examples=["METOKS", "Antooooooon"])
    email: EmailStr | None = Field(None, title="Почта пользователя",
                            description="Принимается любая почта, которая содержит @",
                            examples=["metoks@gmail.com", "trap@abcde.ru"],)

class UserResponseSchema(BaseModel):
    """Схема для получения данных о юзере. Его имя и почта"""
    name: str = Field(min_length=3, title="Имя пользователя",
                      description="Не меньше 3 символов",
                      examples=["METOKS", "Antooooooon"])
    
    email: EmailStr = Field(title="Почта пользователя",
                            description="Принимается любая почта, которая содержит @",
                            examples=["metoks@gmail.com", "trap@abcde.ru"],)

class UserSettingsSchema(BaseModel):
    settings: dict = Field(title="Настройки пользователя",
                           description="Здесь находятся все настройки пользователя в JSON формате",
                           examples=[{}], )

class UserResponseWithSettingsSchema(UserResponseSchema):
    settings: dict = Field(title="Настройки пользователя",)

class UserSettingsResponseSchema(UserSettingsSchema):
    pass

class UpdateUserSettingsSchema(UserSettingsSchema):
    pass

class UserInvitesInfoSchema(BaseModel):
    id: UUID = Field(title="Айди приглашения",)
    user_id: UUID = Field(title="Айди пользователя",
                          description="Айди приглашенного в проект пользователя",)
    project_id: UUID = Field(title="Айди проекта",
                             description="Айди проекта, в который пригласили пользователя",)
    project_name: str = Field(title="Название проекта",)
    project_author_email: EmailStr = Field(title="Почта автора проекта",
                                           examples=["metoks@gmail.com"])

class UserInvitesUpdateSchema(BaseModel):
    status: Literal["accepted", "denied"] = Field(title="Статус приглашения",
                                                  description="Принимается только accepted и deleted",)
