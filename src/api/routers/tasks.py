from fastapi import APIRouter
from fastapi.params import Depends

from src.api.dependencies import get_current_user, get_session
from src.services.tasksServices import TasksService

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.delete("/{task_id}")
async def delete_task(task_id: int, user_id: int = Depends(get_current_user), session = Depends(get_session)):
    service = TasksService(session)
    await service.delete_task(task_id=task_id, user_id=user_id)
    return {"Success": True}