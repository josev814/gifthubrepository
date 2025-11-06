from .models import User, Registry, GiftItem
from .auth import get_password_hash, verify_password
from .database import engine

from fastapi import HTTPException, status
from sqlmodel import select, Session, text
from sqlalchemy import select as sa_select
from sqlalchemy.exc import SQLAlchemyError

def create_user(email: str, password: str, session: Session):
    user = User(email=email, hashed_password=get_password_hash(password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def authenticate_user(email: str, password: str, session: Session):
    q = select(User).where(User.email == email)
    user = session.exec(q).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_registry(owner_id: int, data, session: Session):
    reg = Registry(owner_id=owner_id, name=data.name, occasion=data.occasion, is_public=data.is_public)
    session.add(reg)
    session.commit()
    session.refresh(reg)
    return reg

def add_item_to_registry(registry_id: int, item_data, session: Session):
    item = GiftItem(registry_id=registry_id, title=item_data.title,
                    description=item_data.description,
                    external_link=item_data.external_link,
                    price_cents=item_data.price_cents)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

def search_items(query: str, session: Session, limit: int=50):
    stmt = select(GiftItem).where(GiftItem.title.ilike(f"%{query}%")).limit(limit)
    return session.exec(stmt).all()

# Safe buy: lock the row
def buy_item(item_id: int, user_id: int, session: Session):
    try:
        item = session.exec(
            sa_select(GiftItem).where(GiftItem.id == item_id).with_for_update()
        ).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if item.bought:
            raise HTTPException(status_code=400, detail="Item already bought")
        if item.reserved_by_user_id and item.reserved_by_user_id != user_id:
            raise HTTPException(status_code=400, detail="Item reserved by another user")
        # mark bought
        item.bought = True
        item.reserved_by_user_id = user_id
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error when marking item as purchased") from e

def reserve_item(item_id: int, user_id: int, session: Session):
    item = session.exec(select(GiftItem).where(GiftItem.id == item_id).with_for_update()).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.bought:
        raise HTTPException(status_code=400, detail="Item already bought")
    if item.reserved_by_user_id and item.reserved_by_user_id != user_id:
        raise HTTPException(status_code=400, detail="Item reserved by another user")
    item.reserved_by_user_id = user_id
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

def unreserve_item(item_id: int, user_id: int, session: Session):
    item = session.exec(select(GiftItem).where(GiftItem.id == item_id).with_for_update()).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.bought:
        raise HTTPException(status_code=400, detail="Item already bought")
    if item.reserved_by_user_id != user_id:
        raise HTTPException(status_code=400, detail="Item not reserved by you")
    item.reserved_by_user_id = None
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
