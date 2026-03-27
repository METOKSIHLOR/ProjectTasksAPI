from typing import Literal, List

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.projectSchemas import CreateProjectSchema, ProjectAddMemberSchema
from src.api.schemas.tasksSchemas import TaskInfoSchema
from src.db.models import Project, ProjectMember
from src.db.repositories.projectRepo import ProjectRepository


class ProjectServices:
    def __init__(self, session: AsyncSession):
        self.repo = ProjectRepository(session)

    async def create_new_project(self, project: CreateProjectSchema, user_id: int):
        project = await self.repo.create_project(Project(name=project.name, owner_id=user_id))
        await self.repo.commit()
        return project

    async def get_project_by_id(self, project_id):
        project = await self.repo.get_project_by_id(project_id)
        return project

    async def check_user_role(self, user_id: int, project_id: int, roles: List[Literal["member", "owner"]]):
        correct = await self.repo.check_user_role(user_id, project_id, roles)
        if not correct:
            raise TypeError

    async def add_member(self, project_id: int, user_id: int):
        member = await self.repo.add_member(ProjectMember(project_id=project_id, user_id=user_id))
        await self.repo.commit()
        return member





