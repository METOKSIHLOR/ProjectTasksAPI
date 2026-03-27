from enum import member
from typing import List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.suite.test_reflection import users

from src.api.schemas.tasksSchemas import TaskInfoSchema
from src.db.models import Project, ProjectMember, Task


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_project(self, project: Project):
        self.session.add(project)
        await self.session.flush()

        member = ProjectMember(
            project_id=project.id,
            user_id=project.owner_id,
            role='owner'
        )

        self.session.add(member)
        await self.session.flush()
        return project

    async def get_project_by_id(self, project_id: int):
        stmt = select(Project).where(Project.id == project_id)
        project = await self.session.execute(stmt)
        return project.scalar_one_or_none()

    async def check_user_role(self, user_id, project_id, roles: List) -> bool:
        stmt = select(ProjectMember).where(and_(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id))
        result = await self.session.execute(stmt)
        member = result.scalar_one_or_none()

        if member:
            for i in roles:
                if member.role == i:
                   return True
        return False

    async def add_member(self, member: ProjectMember):
        self.session.add(member)
        await self.session.flush()
        return member


    async def commit(self):
        await self.session.commit()