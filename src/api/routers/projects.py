from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_session
from src.api.schemas.projectSchemas import CreateProjectSchema, ProjectInfoSchema, ProjectMemberSchema, \
    ProjectAddMemberSchema
from src.services.projectServices import ProjectServices
from src.services.userServices import UserServices

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=CreateProjectSchema)
async def create_project(project: CreateProjectSchema,
                         session: AsyncSession = Depends(get_session),
                         user_id: int = Depends(get_current_user)):
    """Ручка обращается к сервису и создает запись в бд о новом проекте"""
    services = ProjectServices(session)
    project = await services.create_new_project(project, user_id)
    return project

@router.get("")
async def get_user_projects(user_id = Depends(get_current_user), session = Depends(get_session)) -> List[ProjectInfoSchema]:
    """Ручка возвращает все проекты конкретного пользователя по его айди, полученного из куков"""
    service = UserServices(session)
    projects = await service.get_user_projects(user_id)
    return projects

@router.get("/{project_id}")
async def get_project_details(project_id: int,
                              session: AsyncSession = Depends(get_session),
                              user_id = Depends(get_current_user)) -> ProjectInfoSchema:
    """Возвращает информацию о проекте по его айди"""
    service = ProjectServices(session)

    """Проверяем имеет ли пользователь доступ (Должен участвовать в проекте чтобы увидеть о нем информацию)"""
    try:
        await service.check_user_role(user_id, project_id, ['member', 'owner'])
    except TypeError:
        raise HTTPException(status_code=403, detail="Not authorized")

    project = await service.get_project_by_id(project_id) # получаем обьект проекта

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project

@router.post("/{project_id}/members")
async def get_project_members(project_id: int, member: ProjectAddMemberSchema,
                              session: AsyncSession = Depends(get_session),
                              user_id = Depends(get_current_user)):
    """Ручка добавляет в указанную группу нового участника, если пользователь является владельцем"""
    service = ProjectServices(session)
    try:
        await service.check_user_role(user_id, project_id, ['owner']) # проверяем является ли пользователь владельцем
    except TypeError:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        await service.add_member(user_id=member.user_id, project_id=project_id)
    except IntegrityError: # если пользователь уже был добавлен в группу (дубликат в бд)
        raise HTTPException(status_code=409, detail="User already added")
    return {"Success": True}