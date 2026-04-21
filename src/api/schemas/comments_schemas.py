import uuid
from datetime import datetime
from uuid import UUID

from typing import Literal
from pydantic import BaseModel, EmailStr, Field, field_serializer


class CommentSchema(BaseModel):
    text: str = Field(title="Текст комментария",
                      description="Должен быть больше 0 и меньше 500 символов",
                      min_length=1,
                      max_length=500,
                      examples=["This task is very HAAAARD"])

class CreateCommentSchema(CommentSchema):
    """Схема для создания комментария. Требуется только текст"""
    replied_to: uuid.UUID | None = Field(None, title="Айди реплая",
                                description="Айди комментария, на который отвечает юзер (опционально)",)

class CommentInfoSchema(CommentSchema):
    """Схема для получения информации о комментарии: Айди, айди его автора и текст"""
    id: UUID = Field(title="Айди комментария", description="Должно быть uuid")

    author_name: str = Field(title="Имя автора комментария")

    author_email: EmailStr = Field(title="Почта автора комментария",
                                   examples=["metoks@gmail.com"])

    replied_to: uuid.UUID | Literal["deleted"] | None = Field(None, title="Айди реплая",
                                description="Айди комментария, на который отвечает юзер (опционально)",)

    created_at: datetime = Field(title="Время создания коммента")

    @field_serializer('created_at')
    def serialize_dt(self, dt: datetime, _info):
        """делаем человекочитаемый формат времени"""
        return dt.strftime('%Y-%m-%d %H:%M:%S')


class CommentUpdateSchema(CommentSchema):
    """Схема для обновления текста комментария"""
    text: str = Field(title="Текст комментария",
                      description="От 1 до 500 символов",
                      min_length=1,
                      max_length=500,
                      examples=[""])