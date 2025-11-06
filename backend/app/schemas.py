from pydantic import BaseModel
from typing import Optional, List

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RegistryCreate(BaseModel):
    name: str
    occasion: Optional[str] = None
    is_public: Optional[bool] = True

class GiftItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    external_link: Optional[str] = None
    price_cents: Optional[int] = None
    created_at: datetime

class GiftItemOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    external_link: Optional[str]
    price_cents: Optional[int]
    reserved_by_user_id: Optional[int]
    bought: bool

class ReservationCreate(BaseModel):
    duration_minutes: int

class ReservationRead(BaseModel):
    id: int
    gift_id: int
    user_id: int
    reserved_at: datetime
    expires_at: datetime
    confirmed: bool
