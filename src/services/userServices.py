from sqlalchemy.ext.asyncio import AsyncSession

from src.api.authorization.hash import hash_password, verify_password
from src.api.authorization.storage import storage
from src.api.schemas.userSchemas import UserRegistrationSchema, UserLoginSchema
from src.db.models import User
from src.db.repositories.userRepo import UserRepository
import uuid

class UserServices:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def register(self, schema: UserRegistrationSchema):
        hash_pw = hash_password(schema.password)
        model = User(name=schema.name, email=schema.email, hash_password=hash_pw)

        user = await self.repo.create_user(model)
        await self.repo.commit()

        return user

    async def auth(self, schema: UserLoginSchema):
        user = await self.repo.get_user_by_email(schema.email)

        if not user or not verify_password(schema.password, user.hash_password):
            raise ValueError

        session_id = str(uuid.uuid4())

        storage.set(session_id, user.id, ex=3600)

        return session_id


    async def get_user_by_id(self, user_id):
        user = await self.repo.get_user_by_id(user_id)
        return user

    async def get_user_projects(self, user_id):
        projects = await self.repo.get_user_projects(user_id)
        return projects

