from pydantic import BaseModel, EmailStr


class UserResponseSchema(BaseModel):
    id: int
    name: str
    email: EmailStr

class UserRegistrationSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str