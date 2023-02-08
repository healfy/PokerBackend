from typing import Any
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from backend.apps.auth import AuthService
from backend.apps.user.schema import UserSchema, UserCreateSchema, UserProfileSchema, WalletSchema
from backend.apps.user.service import UserService
from backend.web.handlers.dependencies import get_user_service, get_auth_service, check_access

router = APIRouter(prefix="/users")


@router.post(
    "/register",
    description="API endpoint for user create",
    response_class=Response,
)
async def register(
    data: UserCreateSchema,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user: UserSchema = await user_service.register(data)
    response = Response()
    response.set_cookie(key="access_token", value=auth_service.encode_access_token(user.id))
    response.set_cookie(key="refresh_token", value=auth_service.encode_refresh_token(user.id))
    return response


@router.post(
    "/{user_id}",
    description="API endpoint for get User profile information",
    response_model=UserProfileSchema,
)
async def get_user_info(
        user_id: int,
        _: Any = Depends(check_access),
        user_service: UserService = Depends(get_user_service),
) -> UserProfileSchema:
    user_info = await user_service.get_user_full_info(user_id)
    return UserProfileSchema(
        email=user_info.email,
        wallet=WalletSchema(
            amount=user_info.wallet.amount,
            currency=user_info.wallet.currency,
        ),
    )
