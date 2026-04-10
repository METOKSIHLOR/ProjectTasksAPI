import uuid

from fastapi import status

from src.core.exceptions.base_exception import BaseAPIException

class ProjectNotFoundException(BaseAPIException):
    def __init__(self, project_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
            error_code="PROJECT_NOT_FOUND",
            extra_data={
                "project_id": str(project_id),
            }
        )

class ProjectMemberConflictException(BaseAPIException):
    def __init__(self, project_id: uuid.UUID, member_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this project",
            error_code="PROJECT_MEMBER_CONFLICT",
            log_message="Member already exists",
            extra_data={
                "project_id": str(project_id),
                "member_id": str(member_id),
            }
        )

class ProjectDeleteConflictException(BaseAPIException):
    def __init__(self, project_id: uuid.UUID, member_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User can't delete himself",
            error_code="PROJECT_DELETE_CONFLICT",
            log_message="Owner tried to delete himself from the project",
            extra_data={
                "project_id": str(project_id),
                "mmeber_id": str(member_id),
            }
        )

class ProjectMemberNotFoundException(BaseAPIException):
    def __init__(self, project_id: uuid.UUID, member_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
            error_code="PROJECT_MEMBER_NOT_FOUND",
            extra_data={
                "project_id": str(project_id),
                "mmeber_id": str(member_id),
            }
        )