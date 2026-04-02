from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_session
from src.api.schemas.tasks_schemas import UpdateTaskSchema, CreateTaskSchema, TaskInfoSchema
from src.services.tasks_services import TasksService

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])

@router.post("", summary="Создать новую таску")
async def create_task(project_id: int,
                              task: CreateTaskSchema,
                            session: AsyncSession = Depends(get_session),
                            user_id: int = Depends(get_current_user)) -> TaskInfoSchema:
    """Создание новой таски в указанном проекте по его айди, если пользователь является создателем проекта"""
    task_serv = TasksService(session)
    task = await task_serv.create_task(project_id=project_id, user_id=user_id, task=task)
    return task

@router.get("", summary="Получить все таски в проекте")
async def get_all_tasks_in_project(project_id: int,
                            session: AsyncSession = Depends(get_session),
                            user_id: int = Depends(get_current_user)) -> List[TaskInfoSchema]:
    """Получение всех тасок в указанном проекте, если пользователь является его участником"""
    task_serv = TasksService(session)
    tasks = await task_serv.get_tasks_by_project_id(project_id=project_id, user_id=user_id)
    return tasks

@router.delete("/{task_id}", summary="Удалить таску")
async def delete_task(
        project_id: int,
        task_id: int,
        user_id: int = Depends(get_current_user),
        session = Depends(get_session)):
    """Удаление таски из проекта и бд, если юзер является создателем проекта"""
    service = TasksService(session)
    await service.delete_task(task_id=task_id, user_id=user_id, project_id=project_id)
    return {"success": True}

@router.patch("/{task_id}", summary="Обновить данные в таске")
async def update_task(project_id: int,
                      task_id: int,
                      new_task: UpdateTaskSchema,
                      user_id: int = Depends(get_current_user),
                      session = Depends(get_session)):
    """Обновление данных о таске, если юзер является создателем проекта. 
    Обновляются только данные в непустых столбцах"""
    service = TasksService(session)
    await service.update_task(task_id=task_id, new_task=new_task, user_id=user_id, project_id=project_id)
    return {"success": True}

