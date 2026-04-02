from fastapi import HTTPException

from src.db.models import Comment
from src.db.repositories.comments_repo import CommentsRepository
from src.services.tasks_services import TasksService


class CommentsServices:
    def __init__(self, session):
        self.repo = CommentsRepository(session)
        self.tasks_service = TasksService(session)

    async def create_comment(self, project_id: int, task_id: int, author_id: int, text: str):
        await self.tasks_service.get_task_check_user_permission_by_task_id(project_id=project_id, task_id=task_id, user_id=author_id,
                                                                           roles=["member", "owner"])
        comment = Comment(task_id=task_id, author_id=author_id, text=text)
        await self.repo.create_comment(comment)
        await self.repo.commit()
        return comment

    async def get_comments(self, project_id: int, task_id: int, user_id: int):
        await self.tasks_service.get_task_check_user_permission_by_task_id(project_id=project_id, task_id=task_id, user_id=user_id,
                                                                           roles=["member", "owner"])
        comments = await self.repo.get_comments(task_id=task_id)
        return comments

    async def update_comment(self, project_id: int, comment_id: int, task_id: int, user_id: int, text: str):
        comment = await self.get_comment_belong_to_task(project_id=project_id, comment_id=comment_id, task_id=task_id)

        if comment.author_id != user_id:
            raise HTTPException(status_code=403, detail="Comment doesn't belong to user")

        await self.repo.update_comment(comment=comment, text=text)
        await self.repo.commit()
        return comment


    async def delete_comment(self, project_id: int, comment_id: int, task_id: int, user_id: int):
        comment = await self.get_comment_belong_to_task(project_id=project_id, comment_id=comment_id, task_id=task_id)

        if comment.author_id != user_id:
            raise HTTPException(status_code=403, detail="Comment doesn't belong to user")

        await self.repo.delete_comment(comment)

        await self.repo.commit()
        return comment

    async def get_comment_belong_to_task(self, comment_id: int, task_id: int, project_id: int):
        await self.tasks_service.check_task_in_this_project(task_id=task_id, project_id=project_id)
        comment = await self.repo.get_comment_in_task(comment_id=comment_id, task_id=task_id)
        if comment is None:
            raise HTTPException(status_code=404, detail="In this task this comment does not exist")
        return comment