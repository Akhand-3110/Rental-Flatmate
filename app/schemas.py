from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from app.models import Role, RequestStatus

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: Role

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[Role] = None

class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: Role
    class Config:
        from_attributes = True

class ListingCreate(BaseModel):
    location: str
    rent: float
    available_from: datetime
    room_type: str
    is_furnished: bool = False
    photos: List[str] = []

class ListingOut(BaseModel):
    id: str
    owner_id: str
    location: str
    rent: float
    available_from: datetime
    room_type: str
    is_furnished: bool
    photos: str
    is_filled: bool
    compatibility_score: Optional[int] = None
    compatibility_explanation: Optional[str] = None
    class Config:
        from_attributes = True

class TenantProfileCreate(BaseModel):
    preferred_location: str
    budget_min: float
    budget_max: float
    move_in_date: datetime

class TenantProfileOut(BaseModel):
    id: str
    tenant_id: str
    preferred_location: str
    budget_min: float
    budget_max: float
    move_in_date: datetime
    class Config:
        from_attributes = True
class InterestStatusEnum(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class InterestStatusUpdate(BaseModel):
    interest_id: str
    status: InterestStatusEnum