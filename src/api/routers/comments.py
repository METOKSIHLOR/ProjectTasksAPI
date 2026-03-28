from typing import List

from fastapi import APIRouter, Depends

from src.api.dependencies import get_current_user, get_session
from src.api.schemas.comments_schemas import CommentInfoSchema, CommentUpdateSchema
from src.services.comments_services import CommentsServices

router = APIRouter(tags=['comments'])

@router.get("/{task_id}/comments")
async def get_comments(task_id: int,
                       user_id: int = Depends(get_current_user),
                       session = Depends(get_session)) -> List[CommentInfoSchema]:
    service = CommentsServices(session)
    comments = await service.get_comments(task_id=task_id, user_id=user_id)
    return comments

@router.patch("/comments/{comment_id}")
async def update_comments(comment_id: int,
                          update: CommentUpdateSchema,
                          user_id: int = Depends(get_current_user),
                          session = Depends(get_session)):
    service = CommentsServices(session)
    await service.update_comment(user_id=user_id, text=update.text, comment_id=comment_id)
    return {"success": True}

@router.delete("/comments/{comment_id}")
async def delete_comments(comment_id: int,
                          user_id: int = Depends(get_current_user),
                          session = Depends(get_session)):
    service = CommentsServices(session)
    await service.delete_comment(comment_id=comment_id, user_id=user_id)
    return {"Success": True}