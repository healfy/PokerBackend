import time
from datetime import datetime

import jwt

from backend.settings import AuthSettings

from .errors import AccessDeniedError, CredentialsError


class AuthService:
    secret: str
    expires_refresh: int
    expires_access: int
    algorithm: str

    def __init__(self, settings: AuthSettings):
        self.secret = settings.secret_key
        self.expires_access = settings.access_token_expires
        self.expires_refresh = settings.refresh_token_expires
        self.algorithm = settings.algorithm

    def encode_access_token(self, user_id) -> str:
        payload = {
            "expires": time.time() + self.expires_access,
            "iat": datetime.utcnow(),
            "scope": "access_token",
            "user_id": user_id,
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm=self.algorithm,
        )

    def decode_access_token(self, token) -> str:
        try:
            payload = jwt.decode(
                token, self.secret, algorithms=[self.algorithm]
            )
            if payload["scope"] == "access_token":
                return payload["user_id"]
            raise AccessDeniedError(message="Scope for the token is invalid")
        except jwt.InvalidTokenError:
            raise AccessDeniedError(message="Invalid token")

    def encode_refresh_token(self, user_id) -> str:
        payload = {
            "expires": time.time() + self.expires_refresh,
            "iat": datetime.utcnow(),
            "scope": "refresh_token",
            "user_id": user_id,
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def refresh_token(self, refresh_token: str) -> str:
        try:
            payload = jwt.decode(
                refresh_token, self.secret, algorithms=[self.algorithm]
            )
            if payload["scope"] == "refresh_token":
                new_token = self.encode_access_token(payload["user_id"])
                return new_token
            raise CredentialsError(message="Invalid scope for token")
        except jwt.ExpiredSignatureError:
            raise CredentialsError(message="Refresh token expired")
        except jwt.InvalidTokenError:
            raise CredentialsError(message="Invalid refresh token")
