from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.db.models import AllowedTaskStatus

class TaskSchema(BaseModel):
    title: str = Field(title="Название таски", 
                       description="Должно быть в пределах от 1 до 25 символов", 
                       min_length=1,
                       max_length=25,
                       examples=["Create Web API"])
    description: str = Field(title="Описание таски",
                             description="Должно быть в пределах от 1 до 200 символов", 
                             min_length=1,
                             max_length=200,
                             examples=["This API should be create tommorow"])

class TaskSchemaWithStatus(TaskSchema):
    status: AllowedTaskStatus = Field(default="todo",
                                  title="Статус задачи",
                                  description='Допустимые значения: [todo, in_progress, done]',
                                  examples=["todo", "in_progress", "done"])

class CreateTaskSchema(TaskSchema):
    """Схема для создания таски. Требуется айди существующего в группе участника, который выполняет задачу"""
    assignee_email: EmailStr = Field(title="Почта исполнителя",
                             description="Почта человека, который должен выполнить таску",
                             examples=["metoks@gmail.com"])

class TaskInfoSchema(TaskSchemaWithStatus):
    """Схема для получения информации о таске"""
    id: UUID = Field(title="Айди таски", description="должно быть uuid")

    assignee_email: EmailStr = Field(title="Почта исполнителя",
                             description="Почта человека, который должен выполнить таску",
                             examples=["metoks@gmail.com"])

class TaskInfoSchemaWithOwnerEmail(TaskInfoSchema):
    project_owner_email: EmailStr = Field(title="Почта владельца проекта",
                                          description="Почта владельца проекта, к которому привязана эта таска",
                                          examples=["metoks@gmail.com"])

class UpdateTaskSchema(TaskSchema):
    """Схема для обновления данных в таске. Для полей которые обновлять не надо оставить None"""
    title: str | None = Field(None, title="Название таски", 
                       description="Если обновлять поле не надо - оставить None", 
                       examples=["Create web API"])
    description: str | None = Field(None, title="Описание таски",
                             description="Если обновлять поле не надо - оставить None", 
                             examples=["This API should be create tommorow"])
    
    status: AllowedTaskStatus | None = Field(None, title="Статус задачи",
                                                   description='Если обновлять поле не надо - оставить None',
                                                   examples=["todo", "in_progress", "done"])
    
    assignee_email: EmailStr | None = Field(None, title="Почта исполнителя",
                             description="Если обновлять поле не надо - оставить None",
                             examples=["metoks@gmail.com"])
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if value is not None and not (1 < len(value) <= 25):
            raise ValueError("The title length must be between 1 and 25 characters")
        return value
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        if value is not None and not (1 < len(value) <= 200):
            raise ValueError("The description length must be from 1 to 200 characters")
        return value
    

