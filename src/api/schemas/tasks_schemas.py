from typing import Literal
from pydantic import BaseModel, Field

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
                             examples=["This API will be create tommorow"])

class TaskSchemaWithStatus(TaskSchema):
    status: AllowedTaskStatus = Field(default="todo",
                                  title="Статус задачи",
                                  description='Допустимые значения: [todo, in_progress, done]',
                                  examples=["todo", "in_progress", "done"])

class CreateTaskSchema(TaskSchema):
    """Схема для создания таски. Требуется айди существующего в группе участника, который выполняет задачу"""
    assignee_id: int = Field(title="Айди исполнителя",
                             description="Айди человека, который должен выполнить таску. 0 < id < 2147483647",
                             gt=0,lt=2147483647)

class TaskInfoSchema(TaskSchemaWithStatus):
    """Схема для получения информации о таске"""
    id: int = Field(title="Айди пользователя",
                    gt=0,lt=2147483647)

    assignee_id: int = Field(title="Айди исполнителя",
                             description="Айди человека, который должен выполнить таску. 0 < id < 2147483647",
                             gt=0,lt=2147483647)

class UpdateTaskSchema(TaskSchema):
    '''Схема для обновления данных в таске. Для полей которые обновлять не надо оставить пустые двойные кавычки ""'''
    title: str = Field(title="Название таски", 
                       description="Если обновлять поле не надо - оставить пустые кавычки", 
                       min_length=0,
                       max_length=25,
                       examples=[""])
    description: str = Field(title="Описание таски",
                             description="Если обновлять поле не надо - оставить пустые кавычки", 
                             min_length=0,
                             max_length=200,
                             examples=[""])
    
    status: Literal[AllowedTaskStatus, ""] = Field(title="Статус задачи",
                                                   description='Если обновлять поле не надо - оставить пустые кавычки',
                                                   examples=["todo", "in_progress", "done"])

    

