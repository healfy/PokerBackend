from fastapi import HTTPException, status


class CredentialsError(HTTPException):
    code: int = status.HTTP_401_UNAUTHORIZED

    def __init__(self, message: str):
        headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(self.code, message, headers)


class AccessDeniedError(CredentialsError):
    code = status.HTTP_403_FORBIDDEN
