import json
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, Request
from starlette.responses import Response

from backend.apps.auth import (
    AuthSchema,
    AuthService,
    CredentialsError,
)
from backend.apps.user.schema import UserSchema
from backend.apps.user.service import UserService
from backend.web.handlers.dependencies import get_auth_service, get_user_service

router = APIRouter(prefix="/auth")


@router.post("/login", response_class=Response)
async def login(
    data: AuthSchema,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
):
    user: Optional[UserSchema] = await user_service.login(data)
    if user is None:
        return CredentialsError(message="Invalid credentials")

    response = Response(content=json.dumps({'user_id': user.id}))
    response.set_cookie(key="access_token", value=auth_service.encode_access_token(user.id), httponly=True)
    response.set_cookie(key="refresh_token", value=auth_service.encode_refresh_token(user.id), httponly=True)
    return response


@router.post("/logout", response_class=Response)
async def logout():
    response = Response()
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


@router.get('/is_auth')
async def is_auth(request: Request, auth_service: AuthService = Depends(get_auth_service)):
    token = request.cookies.get('access_token')
    if token:
        try:
            return auth_service.decode_access_token(token)
        except jwt.ExpiredSignatureError:
            pass
    return None
