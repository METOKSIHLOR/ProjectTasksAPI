from src.db.repositories.comments_repo import CommentsRepository


class CommentsServices:
    def __init__(self, session):
        self.repo = CommentsRepository(session)