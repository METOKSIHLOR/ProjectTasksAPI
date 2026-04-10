from typing import List


from src.api.authorization.hash import hash_password, verify_password
from src.core.exceptions.users_exceptions import  ConflictEmailException, InvalidUserCredentialsException, \
    UserNotFoundException, UserNotAuthorizedException

from src.api.schemas.user_schemas import UserRegistrationSchema, UserCredsSchema
from src.db.models import User
from src.db.redis_storage import storage
from src.db.repositories.user_repo import UserRepository
import uuid
from uuid import UUID

class UserServices:
    def __init__(self, session):
        self.repo = UserRepository(session)

    async def register(self, schema: UserRegistrationSchema):
        hash_pw = hash_password(schema.password)
        model = User(name=schema.name, email=schema.email, hash_password=hash_pw)

        email_exast = await self.repo.get_user_by_email(email=schema.email)

        if email_exast is not None:
             raise ConflictEmailException(email=schema.email)
        
        user = await self.repo.create_user(model)

        await self.repo.commit()

        return user

    async def auth(self, schema: UserCredsSchema):
        user = await self.repo.get_user_by_email(schema.email)

        if user is None or not verify_password(schema.password, user.hash_password):
            raise InvalidUserCredentialsException()

        session_id = str(uuid.uuid4())

        await storage.set("session_id:" + session_id, str(user.id), ex=3600)

        return session_id


    async def get_user_by_email(self, email):
        user = await self.repo.get_user_by_email(email=email)

        if user is None:
            raise UserNotFoundException(user_identifier=email)
        
        return user

    async def get_user_by_id(self, user_id: UUID):
        user = await self.repo.get_user_by_id(user_id=user_id)

        if user is None:
            raise UserNotFoundException(user_identifier=user_id)
        
        return user

    async def update_user_name(self, user_id: UUID, new_name: str):
        user = await self.repo.get_user_by_id(user_id=user_id)

        await self.repo.update_user_name(user=user, new_name=new_name)

        await self.repo.commit()

    async def get_user_projects(self, user_id: UUID):
        projects = await self.repo.get_user_projects(user_id)
        return projects

    async def check_user_role(self, user_id, project_id, roles: List[str]):
        if not await self.repo.check_user_role(user_id=user_id, project_id=project_id, roles=roles):  # проверяем соответствие роли пользователя
            raise UserNotAuthorizedException()

