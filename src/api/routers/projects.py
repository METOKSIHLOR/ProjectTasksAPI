from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import CheckUserPerms, get_current_user, get_session
from src.api.schemas.project_schemas import CreateProjectSchema, UpdateProjectSchema, ProjectInfoSchema, ProjectMemberIdSchema, ProjectResponseSchema
from src.services.project_services import ProjectServices
from src.services.user_services import UserServices
from uuid import UUID

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectResponseSchema, summary="Создать проект",
            responses={
                401: {"description": "Пользователь не залогинен"},
            })
async def create_project(project: CreateProjectSchema,
                         session: AsyncSession = Depends(get_session),
                         user_id: UUID = Depends(get_current_user)):
    """Создание нового проекта"""
    services = ProjectServices(session)
    project = await services.create_new_project(project, user_id)
    return project

@router.delete("/{project_id}", summary="Удалить проект",
            responses={
                401: {"description": "Пользователь не залогинен"},
                403: {"description": "Пользователь не является владельцем проекта"},
            })
async def delete_project(project_id: UUID,
                         session: AsyncSession = Depends(get_session),
                         _: None = Depends(CheckUserPerms(['owner']))):
    """Удаление всего проекта, если юзер является его создателем"""
    services = ProjectServices(session)
    await services.delete_project(project_id)
    return {"success": True}

@router.get("",
            summary="Получить все проекты пользователя", 
            response_model=List[ProjectResponseSchema],
            responses={
                401: {"description": "Пользователь не залогинен"},
            })
async def get_all_user_projects(user_id = Depends(get_current_user), session = Depends(get_session)) -> List[ProjectInfoSchema]:
    """Получение всех проектов конкретного пользователя по его айди, полученному из куков"""
    service = UserServices(session)
    projects = await service.get_user_projects(user_id)
    return projects

@router.get("/{project_id}", summary="Получить данные о проекте",
            responses={
                401: {"description": "Пользователь не залогинен"},
                403: {"description": "Пользователь не является участником проекта"},
                404: {"description": "Проект не был найден"}
            })
async def get_project_details(project_id: UUID,
                              session: AsyncSession = Depends(get_session),
                              _: None = Depends(CheckUserPerms(["member", "owner"]))) -> ProjectInfoSchema:
    """Возвращает название и участников проекта по его айди"""
    service = ProjectServices(session)

    """Проверяем имеет ли пользователь доступ (Должен участвовать в проекте чтобы увидеть о нем информацию)"""
    project = await service.get_project_by_id(project_id=project_id)

    return project

@router.patch("/{project_id}", summary="Обновить название проекта",
            responses={
                401: {"description": "Пользователь не залогинен"},
                403: {"description": "Пользователь не является владельцем проекта"},
                404: {"description": "Проект не был найден"}
            })
async def update_project_name(project_id: UUID,
                                 update: UpdateProjectSchema,
                                 session = Depends(get_session),
                                 _: None = Depends(CheckUserPerms(["owner"]))):
    """Обновление названия проекта, если юзер является его создателем"""
    service = ProjectServices(session)
    await service.update_project_name(project_id=project_id, name=update.name)

    return {"success": True}


@router.post("/{project_id}/members", summary="Добавить участника",
            responses={
                401: {"description": "Пользователь не залогинен"},
                403: {"description": "Пользователь не является владельцем проекта"},
                404: {"description": "Проект не был найден"},
                409: {"description": "Пользователь уже находится в проекте"}
            })
async def add_project_member(project_id: UUID, member: ProjectMemberIdSchema,
                             session: AsyncSession = Depends(get_session),
                             _: None = Depends(CheckUserPerms(["owner"]))):
    """Добавление в указанную группу нового участника, если пользователь является владельцем"""
    service = ProjectServices(session)

    await service.add_member(member_email=member.email, project_id=project_id)

    return {"success": True}

@router.delete("/{project_id}/members", summary="Удалить участника",
            responses={
                401: {"description": "Пользователь не залогинен"},
                403: {"description": "Пользователь не является владельцем проекта | Попытка удалить себя же"},
                404: {"description": "Проект не был найден | Участник не был найден"},
            })
async def remove_project_member(project_id: UUID,
                                member: ProjectMemberIdSchema,
                                session: AsyncSession = Depends(get_session),
                                user_id = Depends(get_current_user),
                                _: None = Depends(CheckUserPerms(["owner"]))):
    """Удаление участника из группы, если таковой в ней присутствует и пользователь является ее создателем"""
    service = ProjectServices(session)
    await service.remove_member(project_id=project_id, member_email=member.email, user_id=user_id)
    return {"success": True}