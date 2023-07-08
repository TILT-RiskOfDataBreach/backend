from enum import Enum
from pydantic import BaseModel


class _Address(BaseModel):
    street: str
    number: str
    zip_code: str
    city: str
    country: str


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str
    access_lvl: int


class NewUser(BaseModel):
    username: str
    password: str
    company: str
    country: str
    address: _Address
    type: str


class User(BaseModel):
    username: str
    password: str
    company: str
    country: str
    address: _Address
    type: str
    access_lvl: int


# 0 Default, can update data sharing network and risk estimates
# 1 Admin, has admin access

class AccessLevels(Enum):
    default = 0,
    admin = 1
