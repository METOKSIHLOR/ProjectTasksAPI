import uuid

from fastapi import HTTPException, status


class BaseUserException(HTTPException):
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

class ConflictEmailException(BaseUserException):
    def __init__(self, email):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="User email already in use",
            error_code="EMAIL_ALREADY_EXISTS",
            log_message="Email registration conflict",
            extra_data={
                "email": email.lower().strip(),
            }
        )

class UserNotFoundException(BaseUserException):
    def __init__(self, user_identifier: uuid.UUID | str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            error_code="USER_NOT_FOUND",
            log_message=f"User {user_identifier} not found in DB",
            extra_data={
                "user_identifier": user_identifier,
            },
        )

class InvalidUserCredentialsException(BaseUserException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            error_code="INVALID_CREDENTIALS",
            log_message="User sent invalid credentials",
        )

class UserNotAuthorizedException(BaseUserException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized",
            error_code="USER_NOT_AUTHORIZED",
        )

class UserNotAuthenticatedException(BaseUserException):
    def __init__(self, user_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authenticated",
            error_code="USER_NOT_AUTHENTICATED",
            extra_data={
                "user_id": user_id
            }
        )