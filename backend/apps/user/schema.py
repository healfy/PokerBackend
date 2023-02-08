import re
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, root_validator, validator

pw_check_regex = re.compile(
    r"^(?=(.*\d){2})(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z\d]).{10,}$"
)


class UserCreateSchema(BaseModel):
    email: EmailStr = Field(title="customer email")
    password: str = Field(
        title="customer password", description="some strong passsword"
    )
    confirm_password: str = Field(title="customer password", description="")

    @root_validator
    def check_passwords_match(cls, values: dict):
        pw1, pw2 = values.get("confirm_password"), values.get("password")
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("passwords do not match")
        return values

    @validator("password", pre=True)
    def check_pwd(cls, v: str):
        if not pw_check_regex.search(v):
            raise ValueError("Password strength is not enough")
        return v


class UserSchema(BaseModel):
    id: int = Field(title="customer unique  identifier")
    email: EmailStr = Field(title="customer email")

    class Config:
        orm_mode = True


class WalletSchema(BaseModel):
    amount: Decimal
    currency: str

    class Config:
        json_encoders = {Decimal: str}


class UserProfileSchema(BaseModel):
    email: EmailStr = Field(title="customer email")
    wallet: WalletSchema
