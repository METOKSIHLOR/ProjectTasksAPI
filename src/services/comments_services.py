from fastapi import HTTPException

from src.db.models import Comment
from src.db.repositories.comments_repo import CommentsRepository
from src.db.repositories.tasks_repo import TasksRepository
from src.services.tasks_services import TasksService


class CommentsServices:
    def __init__(self, session):
        self.repo = CommentsRepository(session)
        self.tasks_service = TasksService(session)

    async def create_comment(self, task_id, author_id, text):
        await self.tasks_service.check_user_permission_by_task_id(task_id=task_id,
                                                                  user_id=author_id,
                                                                  roles=["member", "owner"])
        comment = Comment(task_id=task_id, author_id=author_id, text=text)
        await self.repo.create_comment(comment)
        await self.repo.commit()
        return comment

    async def get_comments(self, task_id, user_id):
        await self.tasks_service.check_user_permission_by_task_id(task_id=task_id,
                                                                  user_id=user_id,
                                                                  roles=["member", "owner"])
        comments = await self.repo.get_comments(task_id=task_id)
        return comments

    async def update_comment(self, comment_id, user_id, text):
        try:
            comment = await self.repo.update_comment(user_id=user_id, text=text, comment_id=comment_id)
        except ValueError as e:
            raise HTTPException(status_code=403, detail=str(e))
        await self.repo.commit()
        return comment

    async def delete_comment(self, comment_id, user_id):
        try:
            comment = await self.repo.delete_comment(comment_id=comment_id, user_id=user_id)
        except ValueError as e:
            raise HTTPException(status_code=403, detail=str(e))
        await self.repo.commit()
        return comment