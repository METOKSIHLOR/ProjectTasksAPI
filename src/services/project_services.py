from typing import Literal, List


from fastapi import HTTPException
from sqlalchemy.exc import DataError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.project_schemas import ProjectSchema, ProjectMemberIdSchema
from src.api.schemas.tasks_schemas import TaskInfoSchema
from src.db.models import Project, ProjectMember
from src.db.repositories.project_repo import ProjectRepository
from src.services.user_services import UserServices


class ProjectServices:
    def __init__(self, session):
        self.repo = ProjectRepository(session)

    async def get_project_and_check_user_permission_by_project_id(self, project_id: int, user_id: int, roles: List[str]):
        project = await self.repo.get_project_by_id(project_id)

        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        user_serv = UserServices(self.repo.session)
        await user_serv.check_user_role(user_id=user_id, project_id=project.id, roles=roles)

        return project

    async def create_new_project(self, project: ProjectSchema, user_id: int):
        project = await self.repo.create_project(Project(name=project.name, owner_id=user_id))
        await self.repo.commit()
        return project

    async def get_project_by_id(self, project_id):
        project = await self.repo.get_project_by_id(project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    async def delete_project(self, project_id, user_id):
        await self.get_project_and_check_user_permission_by_project_id(project_id, user_id, ['owner'])
        project = await self.repo.get_project_by_id(project_id)
        await self.repo.delete_project(project)
        await self.repo.commit()
        return project

    async def get_project_member_by_id(self, project_id, member_id):
        member = await self.repo.get_project_member(project_id, member_id)
        if member is None:
            raise HTTPException(status_code=404, detail="Member not found")
        return member

    async def add_member(self, project_id: int, user_id: int):
        user_serv = UserServices(self.repo.session)
        await user_serv.get_user_by_id(user_id=user_id)
        member = await self.repo.add_member(ProjectMember(project_id=project_id, user_id=user_id))
        await self.repo.commit()
        return member

    async def remove_member(self, project_id: int, member_id: int, user_id: int):
        await self.get_project_and_check_user_permission_by_project_id(project_id=project_id, user_id=user_id,
                                                                       roles=["owner"])
        if member_id == user_id:
            raise HTTPException(status_code=403, detail="Self delete does not allow")

        member = await self.repo.get_project_member(project_id, member_id)

        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        await self.repo.remove_member(member=member)
        await self.repo.commit()
        return member

    async def update_project_name(self, user_id: int, project_id: int, name: str):
        project = await self.get_project_and_check_user_permission_by_project_id(project_id=project_id, user_id=user_id,
                                                                                 roles=["owner"])
        project = await self.repo.update_project_name(project=project, name=name)
        await self.repo.commit()
        return project





