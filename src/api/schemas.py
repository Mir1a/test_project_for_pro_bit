# region -----External Imports-----
from datetime import datetime
from typing import Optional
import re
from pydantic import BaseModel, EmailStr, field_validator, constr
# endregion


# region -----Auth Schemas-----
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user_id: Optional[int] = None
    context: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AccessToken(BaseModel):
    access_token: str
# endregion


# region -----Core User Schemas-----
class CoreUserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, password):
        if not password:
            raise ValueError("Password is required")
        if len(password) < 8:
            raise ValueError("Password must contain at least 8 characters")
        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'\d', password):
            raise ValueError("Password must contain at least one digit")
        return password


class CoreUserResponse(BaseModel):
    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
# endregion


# region -----Tenant User Schemas-----
class TenantUserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, password):
        if not password:
            raise ValueError("Password is required")
        if len(password) < 8:
            raise ValueError("Password must contain at least 8 characters")
        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'\d', password):
            raise ValueError("Password must contain at least one digit")
        return password


class TenantUserResponse(BaseModel):
    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TenantUserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
# endregion


# region -----Organization Schemas-----
class OrganizationCreate(BaseModel):
    name: constr(min_length=2, max_length=255)
    slug: constr(min_length=2, max_length=100, pattern=r'^[a-z0-9-]+$')
    description: Optional[str] = None

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, slug):
        if not re.match(r'^[a-z0-9-]+$', slug):
            raise ValueError("Slug can only contain lowercase letters, numbers, and hyphens")
        return slug


class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    database_name: str

    class Config:
        from_attributes = True
# endregion
