from typing import Literal
from pydantic import BaseModel, Field

from src.db.models import AllowedTaskStatus

class TaskSchema(BaseModel):
    title: str = Field(title="Название таски", 
                       description="Должно быть в пределах от 1 до 25 символов", 
                       min_length=1,
                       max_length=25)
    description: str = Field(title="Описание таски",
                             description="Должно быть в пределах от 1 до 200 символов", 
                             min_length=1,
                             max_length=200)

class TaskSchemaWithStatus(TaskSchema):
    status: AllowedTaskStatus = Field(default="todo",
                                  title="Статус задачи",
                                  description='Допустимые значения: [todo, in_progress, done]')

class CreateTaskSchema(TaskSchema):
    """Схема для создания таски. Требуется айди существующего в группе участника, который выполняет задачу"""
    assignee_id: int = Field(title="Айди исполнителя",
                             description="Айди человека, который должен выполнить таску. 0 < id < 2147483647",
                             gt=0,lt=2147483647)

class TaskInfoSchema(TaskSchemaWithStatus):
    """Схема для получения информации о таске"""
    id: int
    assignee_id: int = Field(title="Айди исполнителя",
                             description="Айди человека, который должен выполнить таску. 0 < id < 2147483647",
                             gt=0,lt=2147483647)

class UpdateTaskSchema(TaskSchema):
    '''Схема для обновления данных в таске. Для поля которое обновлять не надо оставить пустые двойные кавычки ""'''
    status: Literal[AllowedTaskStatus, ""] = Field(title="Статус задачи",
                                                   description='Для поля которое не требуется обновлять оставьте ""')

    

