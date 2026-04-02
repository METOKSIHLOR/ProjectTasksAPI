from pydantic import BaseModel, Field

class CommentSchema(BaseModel):
    text: str = Field(title="Текст комментария",
                      description="Должен быть больше 0 и меньше 500 символов",
                      gt=0,
                      lt=500,
                      examples=["This task is very HAAAARD"])

class CreateCommentSchema(CommentSchema):
    """Схема для создания комментария. Требуется только текст"""
    pass

class CommentInfoSchema(CommentSchema):
    """Схема для получения информации о комментарии: Айди, айди его автора и текст"""
    id: int = Field(title="Айди комментария")
    author_id: int = Field(title="Айди автора комментария")


class CommentUpdateSchema(CommentSchema):
    """Схема для обновления текста комментария"""
    pass