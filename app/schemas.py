
print("----------------------Entered schemas-----------------------")
from pydantic import BaseModel
from typing import Optional
from enum import Enum

print("UserLevel")
class UserLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    expert = "expert"


class UserBase(BaseModel):
    email: str
    username: str
    age: Optional[int] = None
    level: UserLevel = UserLevel.beginner


class UserIn(UserBase):
    password: str

print("UserLevel")
class UserInDBBase(UserBase):
    id: int
    print("UserInDBBase")

    class Config:
        print("Config")
        orm_mode = True


class UserInDB(UserInDBBase):
    hashed_password: str


class TokenData(BaseModel):
    username: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str

class ConversationQuery(BaseModel):
    query: str
