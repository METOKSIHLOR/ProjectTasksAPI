from enum import member
from typing import List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.suite.test_reflection import users

from src.api.schemas.tasks_schemas import TaskInfoSchema
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
        if not project:
            raise ValueError("Project not found")
        return project.scalar_one_or_none()

    async def is_user_member(self, user_id: int, project_id: int) -> bool:
        stmt = select(ProjectMember).where(
            ProjectMember.user_id == user_id,
            ProjectMember.project_id == project_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def add_member(self, member: ProjectMember):
        self.session.add(member)
        await self.session.flush()
        return member

    async def update_project_name(self, user_id: int, project_id: int, name: str):
        project = await self.get_project_by_id(project_id)
        project.name = name
        await self.session.flush()
        return project


    async def commit(self):
        await self.session.commit()