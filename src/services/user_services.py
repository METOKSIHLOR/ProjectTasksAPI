from typing import List

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.api.authorization.hash import hash_password, verify_password
from src.api.authorization.storage import storage
from src.api.schemas.user_schemas import UserRegistrationSchema, UserCredsSchema
from src.db.models import User
from src.db.repositories.user_repo import UserRepository
import uuid

class UserServices:
    def __init__(self, session):
        self.repo = UserRepository(session)

    async def register(self, schema: UserRegistrationSchema):
        hash_pw = hash_password(schema.password)
        model = User(name=schema.name, email=schema.email, hash_password=hash_pw)

        try:
            user = await self.repo.create_user(model)
        except IntegrityError:  # если почта уже занята
            raise HTTPException(status_code=409, detail="This email already exists")

        await self.repo.commit()

        return user

    async def auth(self, schema: UserCredsSchema):
        user = await self.repo.get_user_by_email(schema.email)

        if user is None or not verify_password(schema.password, user.hash_password):
            raise HTTPException(status_code=401, detail="Incorrect email or password")

        session_id = str(uuid.uuid4())

        await storage.set(session_id, user.id, ex=3600)

        return session_id


    async def get_user_by_email(self, email: str):
        user = await self.repo.get_user_by_email(email=email)

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user

    async def get_user_by_id(self, user_id: int):
        user = await self.repo.get_user_by_id(user_id=user_id)

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user

    async def get_user_projects(self, user_id):
        projects = await self.repo.get_user_projects(user_id)
        return projects

    async def check_user_role(self, user_id, project_id, roles: List[str]) -> bool:
        if not await self.repo.check_user_role(user_id=user_id, project_id=project_id, roles=roles):  # проверяем соответствие роли пользователя
            raise HTTPException(status_code=403, detail="Not authorized")
        return True


