from typing import Optional
from decimal import Decimal
from passlib.context import CryptContext

from backend.core.service import AbstractService
from backend.core.database.repository import PostgresRepository
from backend.apps.auth import AuthSchema, CredentialsError


from .errors import UserAlreadyExistsError
from .models import User, Wallet
from .schema import UserCreateSchema, UserSchema


class UserService(AbstractService):
    pwd_context: CryptContext

    def __init__(self, repository: PostgresRepository):
        self.repository = repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def register(self, data: UserCreateSchema) -> UserSchema:
        async with self.repository.atomic():
            if await self.repository.find_one(User, custom_filter=[User.email == data.email]):
                raise UserAlreadyExistsError(
                    f"Provided email {data.email} is already exists"
                )
            data.password = self.encode_password(data.password)
            result: User = await self.repository.save(
                User, values=data.dict(exclude_unset=True, exclude={"confirm_password"})
            )
            await self.repository.save(Wallet, values={
                'user_id': result.id, 'amount': Decimal('10.00')
            })
        return UserSchema(
            id=result.id,
            email=result.email
        )

    async def login(self, data: AuthSchema) -> Optional[UserSchema]:
        user: User = await self.repository.find_one(User, custom_filter=[User.email == data.email])
        if not user:
            raise CredentialsError(message="User not found")
        if not self.verify_password(data.password, user.password):
            raise CredentialsError(message="Invalid credentials")
        return UserSchema.from_orm(user)

    async def get_user(self, user_id: int)-> Optional[User]:
        return await self.repository.find_one(User, custom_filter=[User.id == user_id])

    async def get_user_full_info(self, user_id: int) -> Optional[User]:
        return await self.repository.find_with_join(User, User.wallet, custom_filter=[User.id == user_id])

    def encode_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, encoded_password: str) -> bool:
        return self.pwd_context.verify(password, encoded_password)
