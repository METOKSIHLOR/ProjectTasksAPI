from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from src.api.schemas.user_schemas import UpdateUserSettingsSchema
from src.db.models import User, Project, ProjectMember, UserInvite


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: User):
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_user_profile(self, user: User, new_details: dict):
        for key, value in new_details.items():
            if value is not None:
                setattr(user, key, value)

        await self.session.flush()
        return user

    async def update_user_settings(self, user: User, new_data: dict):
        user.settings.settings = new_data["settings"]
        await self.session.refresh(user)
        return user

    async def get_user_by_id(self, user_id: UUID):
        user = await self.session.execute(select(User).where(User.id == user_id).options(selectinload(User.settings)))
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email):
        user = await self.session.execute(select(User).where(User.email == email))
        return user.scalar_one_or_none()

    async def get_user_projects(self, user_id: UUID):
        stmt = (
            select(Project)
            .join(ProjectMember)
            .where(ProjectMember.user_id == user_id).order_by(Project.created_at)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_user_invite(self, invite: UserInvite):
        self.session.add(invite)
        await self.session.flush()
        return invite

    async def get_user_invites(self, user_id: UUID):
        stmt = (select(UserInvite).where(and_(UserInvite.user_id == user_id, UserInvite.status == "waiting"))
                .options(selectinload(UserInvite.project).selectinload(Project.owner)))
        invites = await self.session.execute(stmt)
        return invites.scalars().all()

    async def get_user_invite_by_id(self, invite_id: UUID, user_id: UUID):
        stmt = select(UserInvite).where(and_(UserInvite.id == invite_id, UserInvite.user_id == user_id, UserInvite.status == "waiting"))
        invite = await self.session.execute(stmt)
        return invite.scalar_one_or_none()

    async def get_user_invite_by_project_id(self, project_id: UUID, user_id: UUID):
        stmt = select(UserInvite).where(and_(UserInvite.project_id == project_id, UserInvite.user_id == user_id, UserInvite.status == "waiting"))
        invite = await self.session.execute(stmt)
        return invite.scalar_one_or_none()

    async def update_invite_status(self, invite: UserInvite, new_detail: dict):
        invite.status = new_detail["status"]
        await self.session.flush()
        return invite

    async def check_user_role(self, user_id: UUID, project_id: UUID, roles: List[str]) -> bool:
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

