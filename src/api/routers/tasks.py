from fastapi import APIRouter
from fastapi.params import Depends

from src.api.dependencies import get_current_user, get_session
from src.api.schemas.tasks_schemas import UpdateTaskSchema
from src.services.tasks_services import TasksService

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.delete("/{task_id}")
async def delete_task(task_id: int, user_id: int = Depends(get_current_user), session = Depends(get_session)):
    service = TasksService(session)
    await service.delete_task(task_id=task_id, user_id=user_id)
    return {"Success": True}

@router.patch("/{task_id}")
async def update_task(task_id: int,
                      new_task: UpdateTaskSchema,
                      user_id: int = Depends(get_current_user),
                      session = Depends(get_session)):
    service = TasksService(session)
    await service.update_task(task_id=task_id, new_task=new_task, user_id=user_id)
    return {"Success": True}

@router.get("/{task_id}/comments")