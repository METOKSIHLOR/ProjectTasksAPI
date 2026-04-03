from pydantic import BaseModel, EmailStr, Field

class CommentSchema(BaseModel):
    text: str = Field(title="Текст комментария",
                      description="Должен быть больше 0 и меньше 500 символов",
                      min_length=1,
                      max_length=500,
                      examples=["This task is very HAAAARD"])

class CreateCommentSchema(CommentSchema):
    """Схема для создания комментария. Требуется только текст"""
    pass

class CommentInfoSchema(CommentSchema):
    """Схема для получения информации о комментарии: Айди, айди его автора и текст"""
    id: int = Field(title="Айди комментария")
    author_name: str = Field(title="Имя автора комментария")
    author_email: EmailStr = Field(title="Почта автора комментария",
                                   examples=["metoks@gmail.com"])


class CommentUpdateSchema(CommentSchema):
    """Схема для обновления текста комментария"""
    text: str = Field(title="Текст комментария",
                      description="От 1 до 500 символов",
                      min_length=1,
                      max_length=500,
                      examples=[""])