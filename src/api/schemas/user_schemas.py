from dataclasses import field
from pydantic import Field
from pydantic import BaseModel, EmailStr

class UserCredsSchema(BaseModel):
    email: EmailStr = Field(title="Почта пользователя",
                            description="Принимается любая почта, которая содержит @",
                            examples=["metoks@gmail.com", "trap@abcde.ru"],)
    
    password: str = Field(min_length=5,
                          title="Пароль пользователя",
                          description="Пароль должен быть >= 5 символов",
                          examples=["abcdef", "qwerty229"])

class UserRegistrationSchema(UserCredsSchema):
    name: str = Field(min_length=3, title="Имя пользователя",
                      description="Не меньше 3 символов",
                      examples=["METOKS", "Antooooooon"])
    
class UserResponseSchema(BaseModel):

    id: int = Field(title="Айди пользователя")
    name: str = Field(min_length=3, title="Имя пользователя",
                      description="Не меньше 3 символов",
                      examples=["METOKS", "Antooooooon"])
    
    email: EmailStr = Field(title="Почта пользователя",
                            description="Принимается любая почта, которая содержит @",
                            examples=["metoks@gmail.com", "trap@abcde.ru"],)

