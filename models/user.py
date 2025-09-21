from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from datetime import datetime

# Definimos los roles disponibles en el sistema
UserRole = Literal["admin", "store_owner", "buyer", "delivery"]

class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    profile_image: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: UserRole = "buyer"

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    profile_image: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: str
    role: UserRole
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True
