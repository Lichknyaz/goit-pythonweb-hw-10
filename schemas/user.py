from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class UserModel(BaseModel):
    name: str
    email: EmailStr
    phone: str
    birthday: date
    password: str

    class Config:
        orm_mode = True

class UserUpdateModel(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    birthday: Optional[date]

class ResponseUserModel(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    birthday: date
    avatar: Optional[str]
    confirmed: bool

    class Config:
        orm_mode = True