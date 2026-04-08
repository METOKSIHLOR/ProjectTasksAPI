import uuid

from fastapi import HTTPException, status


class BaseProjectException(HTTPException):
    def __init__(
        self,
        *,
        status_code: int,
        detail: str,
        error_code: str,
        extra_data: dict | None = None,
        log_message: str | None = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra_data = extra_data or {}
        self.log_message = log_message or detail

class ProjectNotFoundException(BaseProjectException):
    def __init__(self, project_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
            error_code="PROJECT_NOT_FOUND",
            extra_data={
                "project_id": project_id,
            }
        )

class ProjectMemberConflictException(BaseProjectException):
    def __init__(self, project_id: uuid.UUID, member_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this project",
            error_code="PROJECT_MEMBER_CONFLICT",
            log_message="Member already exists",
            extra_data={
                "project_id": project_id,
                "member_id": member_id,
            }
        )

class ProjectDeleteConflictException(BaseProjectException):
    def __init__(self, project_id: uuid.UUID, member_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User can't delete himself",
            error_code="PROJECT_DELETE_CONFLICT",
            log_message="Owner tried to delete himself from the project",
            extra_data={
                "project_id": project_id,
                "mmeber_id": member_id,
            }
        )

class ProjectMemberNotFoundException(BaseProjectException):
    def __init__(self, project_id: uuid.UUID, member_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
            error_code="PROJECT_MEMBER_NOT_FOUND",
            extra_data={
                "project_id": project_id,
                "mmeber_id": member_id,
            }
        )