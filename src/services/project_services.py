from uuid import UUID


from src.core.exceptions.project_exceptions import ProjectMemberConflictException, ProjectDeleteConflictException, \
    ProjectMemberNotFoundException, ProjectNotFoundException
from src.api.schemas.project_schemas import ProjectSchema
from src.db.models import Project, ProjectMember
from src.db.repositories.project_repo import ProjectRepository
from src.services.user_services import UserServices


class ProjectServices:
    def __init__(self, session):
        self.repo = ProjectRepository(session)
        self.user_serv = UserServices(session=session)

    async def create_new_project(self, project: ProjectSchema, user_id: UUID):
        project = await self.repo.create_project(Project(name=project.name, owner_id=user_id))
        await self.repo.commit()
        return project

    async def get_project_by_id(self, project_id: UUID):
        project = await self.repo.get_project_by_id(project_id)

        if project is None:
            raise ProjectNotFoundException(project_id=project_id)

        return project

    async def delete_project(self, project_id: UUID):
        project = await self.get_project_by_id(project_id)
        
        await self.repo.delete_project(project)
        await self.repo.commit()

        return project

    async def get_project_member_by_id(self, project_id: UUID, member_id: UUID):
        member = await self.repo.get_project_member(project_id=project_id, member_id=member_id)

        if member is None:
            raise ProjectMemberNotFoundException(project_id=project_id, member_id=member_id)

        return member
    
    async def find_project_member_by_email(self, project_id: UUID, member_email):
        user = await self.user_serv.get_user_by_email(member_email)
        return await self.repo.get_project_member(
            project_id=project_id,
            member_id=user.id
        )

    async def add_member(self, member_email, project_id: UUID):
        project = await self.get_project_by_id(project_id=project_id)
        
        member = await self.user_serv.get_user_by_email(member_email)

        existing = await self.repo.get_project_member(
            project_id=project.id,
            member_id=member.id
        )

        if existing:
            raise ProjectMemberConflictException(project_id=project.id, member_id=member.id)

        member = await self.repo.add_member(
            ProjectMember(project_id=project.id, user_id=member.id)
        )

        await self.repo.commit()
        return member

    async def remove_member(self, project_id: UUID, member_email, user_id: UUID):
        member = await self.user_serv.get_user_by_email(email=member_email) # Получаем обьект пользователя по его почте

        if str(member.id) == str(user_id):
            raise ProjectDeleteConflictException(project_id=project_id, member_id=member.id)

        project_member = await self.repo.get_project_member(project_id=project_id, member_id=member.id) # проверяем является ли пользователь участником проекта

        if project_member is None:
            raise ProjectMemberNotFoundException(project_id=project_id, member_id=member.id)

        await self.repo.remove_member(member=project_member)
        await self.repo.commit()
        return member

    async def update_project_name(self, project_id: UUID, name: str):
        project = await self.get_project_by_id(project_id=project_id)
        project = await self.repo.update_project_name(project=project, name=name)
        await self.repo.commit()
        return project





