from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_session
from src.api.schemas.project_schemas import CreateProjectSchema, UpdateProjectSchema, ProjectInfoSchema, ProjectMemberIdSchema, ProjectResponseSchema
from src.services.project_services import ProjectServices
from src.services.user_services import UserServices

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectResponseSchema, summary="Создать проект")
async def create_project(project: CreateProjectSchema,
                         session: AsyncSession = Depends(get_session),
                         user_id: int = Depends(get_current_user)):
    """Создание нового проекта"""
    services = ProjectServices(session)
    project = await services.create_new_project(project, user_id)
    return project

@router.delete("/{project_id}", summary="Удалить проект")
async def delete_project(project_id: int,
                         session: AsyncSession = Depends(get_session),
                         user_id: int = Depends(get_current_user)):
    """Удаление всего проекта, если юзер является его создателем"""
    services = ProjectServices(session)
    await services.delete_project(project_id, user_id)
    return {"success": True}

@router.get("", summary="Получить все проекты пользователя", response_model=List[ProjectResponseSchema])
async def get_all_user_projects(user_id = Depends(get_current_user), session = Depends(get_session)) -> List[ProjectInfoSchema]:
    """Получение всех проектов конкретного пользователя по его айди, полученному из куков"""
    service = UserServices(session)
    projects = await service.get_user_projects(user_id)
    return projects

@router.get("/{project_id}", summary="Получить данные о проекте")
async def get_project_details(project_id: int,
                              session: AsyncSession = Depends(get_session),
                              user_id = Depends(get_current_user)) -> ProjectInfoSchema:
    """Возвращает название и участников проекта по его айди"""
    service = ProjectServices(session)

    """Проверяем имеет ли пользователь доступ (Должен участвовать в проекте чтобы увидеть о нем информацию)"""
    project = await service.get_project_and_check_user_permission_by_project_id(user_id, project_id,
                                                                                ["member", "owner"])

    return project

@router.patch("/{project_id}", summary="Обновить имя проекта")
async def update_project_name(project_id: int,
                                 update: UpdateProjectSchema,
                                 user_id = Depends(get_current_user),
                                 session = Depends(get_session),):
    """Обновление названия проекта, если юзер является его создателем"""
    service = ProjectServices(session)
    await service.update_project_name(user_id=user_id, project_id=project_id, name=update.name)

    return {"success": True}


@router.post("/{project_id}/members", summary="Добавить участника")
async def add_project_member(project_id: int, member: ProjectMemberIdSchema,
                             session: AsyncSession = Depends(get_session),
                             user_id = Depends(get_current_user)):
    """Добавление в указанную группу нового участника, если пользователь является владельцем"""
    service = ProjectServices(session)
    await service.get_project_and_check_user_permission_by_project_id(project_id=project_id, user_id=user_id,
                                                                      roles=["owner"])

    try:
        await service.add_member(user_id=member.user_id, project_id=project_id)
    except IntegrityError: # если пользователь уже был добавлен в группу (дубликат в бд)
        raise HTTPException(status_code=409, detail="User is already a member of this project")
    return {"success": True}

@router.delete("/{project_id}/members", summary="Удалить участника")
async def remove_project_member(project_id: int,
                                member: ProjectMemberIdSchema,
                                session: AsyncSession = Depends(get_session),
                                user_id = Depends(get_current_user)):
    """Удаление участника из группы, если таковой в ней присутствует и пользователь является ее создателем"""
    service = ProjectServices(session)
    await service.remove_member(project_id=project_id, member_id=member.user_id, user_id=user_id)
    return {"success": True}