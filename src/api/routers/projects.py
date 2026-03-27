from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_session
from src.api.schemas.projectSchemas import CreateProjectSchema, ProjectInfoSchema, ProjectMemberSchema, \
    ProjectAddMemberSchema
from src.api.schemas.tasksSchemas import TaskInfoSchema, CreateTaskSchema
from src.services.projectServices import ProjectServices
from src.services.tasksServices import TasksService
from src.services.userServices import UserServices

router = APIRouter(prefix="/projects", tags=["projects"])
async def check_user_role(service, user_id, project_id, roles: List[str]) -> bool:
    try:
        await service.check_user_role(user_id, project_id, roles)  # проверяем является ли пользователь владельцем
    except TypeError:
        raise HTTPException(status_code=403, detail="Not authorized")
    return True

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
    await check_user_role(service, user_id, project_id, ["member", "owner"])

    project = await service.get_project_by_id(project_id) # получаем обьект проекта

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project

@router.post("/{project_id}/members")
async def add_project_member(project_id: int, member: ProjectAddMemberSchema,
                              session: AsyncSession = Depends(get_session),
                              user_id = Depends(get_current_user)):
    """Ручка добавляет в указанную группу нового участника, если пользователь является владельцем"""
    service = ProjectServices(session)
    await check_user_role(service, user_id, project_id, ["member", "owner"])

    try:
        await service.add_member(user_id=member.user_id, project_id=project_id)
    except IntegrityError: # если пользователь уже был добавлен в группу (дубликат в бд)
        raise HTTPException(status_code=409, detail="User already added")
    return {"Success": True}

@router.post("/{project_id}/tasks")
async def create_project_task(project_id: int,
                              task: CreateTaskSchema,
                            session: AsyncSession = Depends(get_session),
                            user_id = Depends(get_current_user)) -> TaskInfoSchema:
    proj_serv = ProjectServices(session)
    task_serv = TasksService(session)
    await check_user_role(proj_serv, user_id, project_id, ["owner"])
    try:
        task = await task_serv.create_task(project_id=project_id, task=task)
    except IntegrityError:
        raise HTTPException(status_code=404, detail="Assignee doens't exists")
    return task

@router.get("/{project_id}/tasks")
async def get_project_tasks(project_id: int,
                            session: AsyncSession = Depends(get_session),
                            user_id = Depends(get_current_user)) -> List[TaskInfoSchema]:
    proj_serv = ProjectServices(session)
    task_serv = TasksService(session)
    await check_user_role(proj_serv, user_id, project_id, ["member", "owner"])
    tasks = await task_serv.get_tasks_by_project_id(project_id)
    return tasks