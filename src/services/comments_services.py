from src.db.models import Comment
from src.db.repositories.comments_repo import CommentsRepository


class CommentsServices:
    def __init__(self, session):
        self.repo = CommentsRepository(session)

    async def create_comment(self, task_id, author_id, text):
        comment = Comment(task_id=task_id, author_id=author_id, text=text)
        await self.repo.create_comment(comment)
        await self.repo.commit()
        return comment
