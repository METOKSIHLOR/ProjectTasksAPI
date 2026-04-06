from typing import List

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.db.models import User, Project, ProjectMember


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: User):
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_user_by_id(self, user_id: int):
        user = await self.session.execute(select(User).where(User.id == user_id))
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: EmailStr):
        user = await self.session.execute(select(User).where(User.email == email))
        return user.scalar_one_or_none()

    async def get_user_projects(self, user_id: int):
        stmt = (
            select(Project)
            .join(ProjectMember)
            .where(ProjectMember.user_id == user_id).order_by(Project.id)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def check_user_role(self, user_id, project_id, roles: List[str]) -> bool:
        stmt = select(ProjectMember).where(and_(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id))
        result = await self.session.execute(stmt)
        member = result.scalar_one_or_none()

        if member:
            for i in roles:
                if member.role == i:
                   return True
        return False


    async def commit(self):
        await self.session.commit()

