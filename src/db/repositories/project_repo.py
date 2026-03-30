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
        return project.scalar_one_or_none()

    async def delete_project(self, project: Project):
        await self.session.delete(project)
        await self.session.flush()
        return project

    async def add_member(self, member: ProjectMember):
        self.session.add(member)
        await self.session.flush()
        return member

    async def get_project_member(self, project_id: int, member_id):
        stmt = select(ProjectMember).where(and_(ProjectMember.project_id == project_id, ProjectMember.user_id == member_id))
        member = await self.session.execute(stmt)
        if not member:
            raise ValueError("Project member not found")
        return member.scalar_one_or_none()

    async def remove_member(self, project_id: int, member_id: int):
        member = await self.get_project_member(project_id, member_id)
        await self.session.delete(member)
        await self.session.flush()
        return member

    async def update_project_name(self, project_id: int, name: str):
        project = await self.get_project_by_id(project_id)
        project.name = name
        await self.session.flush()
        return project


    async def commit(self):
        await self.session.commit()