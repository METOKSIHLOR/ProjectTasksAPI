from typing import Literal, List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.project_schemas import CreateProjectSchema, ProjectAddMemberSchema
from src.api.schemas.tasks_schemas import TaskInfoSchema
from src.db.models import Project, ProjectMember
from src.db.repositories.project_repo import ProjectRepository
from src.services.user_services import UserServices


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

    async def check_user_permission_by_project_id(self, project_id: int, user_id: int, roles: List[str]):
        project = await self.repo.get_project_by_id(project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        user_serv = UserServices(self.repo.session)
        await user_serv.check_user_role(user_id=user_id, project_id=project_id, roles=roles)

        return project

    async def add_member(self, project_id: int, user_id: int):
        user_serv = UserServices(self.repo.session)
        user = await user_serv.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        member = await self.repo.add_member(ProjectMember(project_id=project_id, user_id=user_id))
        await self.repo.commit()
        return member

    async def is_user_member_of_project(self, user_id: int, project_id: int):
        if not await self.repo.is_user_member(user_id, project_id):
            raise HTTPException(status_code=404, detail="User is not member of project")




