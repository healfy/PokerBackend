from typing import Optional

from fastapi import HTTPException, status


class UserServiceException(HTTPException):
    code: int
    message: str

    def __init__(self, message: Optional[str]):
        message = message or self.message
        super().__init__(self.code, message, self.headers)


class UserAlreadyExistsError(UserServiceException):
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    headers = {}
