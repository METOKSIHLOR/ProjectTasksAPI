from src.db.models import Comment


class CommentsRepository:
    def __init__(self, session):
        self.session = session

    async def create_comment(self, comment: Comment):
        self.session.add(comment)
        await self.session.flush()
        return comment

    async def commit(self):
        await self.session.commit()
