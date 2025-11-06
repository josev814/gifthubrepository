from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
import uuid

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    registries: List["Registry"] = Relationship(back_populates="owner")

class Registry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    occasion: Optional[str] = None
    owner_id: int = Field(foreign_key="user.id")
    is_public: bool = Field(default=True)
    share_id: str = Field(default_factory=lambda: str(uuid.uuid4()), index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owner: Optional[User] = Relationship(back_populates="registries")
    items: List["GiftItem"] = Relationship(back_populates="registry")

class GiftItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    registry_id: int = Field(foreign_key="registry.id")
    title: str
    description: Optional[str] = None
    url: str
    price_cents: Optional[int] = None
    reserved_by_user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    bought: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    registry: Optional[Registry] = Relationship(back_populates="items")
    reservation: Optional[Reservation] = Relationship(back_populates="gift")

class Reservation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    gift_id: int = Field(foreign_key="giftitem.id")
    user_id: int = Field(foreign_key="user.id")
    reserved_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    confirmed: bool = Field(default=False)

    gift: GiftItem = Relationship(back_populates="reservations")
