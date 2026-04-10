import uuid

from fastapi import status

from src.core.exceptions.base_exception import BaseAPIException


class ConflictEmailException(BaseAPIException):
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

class UserNotFoundException(BaseAPIException):
    def __init__(self, user_identifier: uuid.UUID | str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            error_code="USER_NOT_FOUND",
            log_message=f"User {user_identifier} not found in DB",
            extra_data={
                "user_identifier": str(user_identifier),
            },
        )

class InvalidUserCredentialsException(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            error_code="INVALID_CREDENTIALS",
            log_message="User sent invalid credentials",
        )

class UserNotAuthorizedException(BaseAPIException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized",
            error_code="USER_NOT_AUTHORIZED",
        )

class UserNotAuthenticatedException(BaseAPIException):
    def __init__(self, user_id: uuid.UUID):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authenticated",
            error_code="USER_NOT_AUTHENTICATED",
            extra_data={
                "user_id": str(user_id)
            }
        )