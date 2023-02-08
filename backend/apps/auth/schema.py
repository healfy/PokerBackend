from pydantic import BaseModel, EmailStr


class TokensSchema(BaseModel):
    access_token: str


class AuthSchema(BaseModel):
    email: EmailStr
    password: str
