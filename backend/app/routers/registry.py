from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import Registry, GiftItemOut, GiftItem
from ..schemas import GiftItemOut
from ..auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix='/api/registries', tags=['registries'])

class RegistryCreate(BaseModel):
    name: str
    occasion: str | None = None
    is_public: bool = True

class GiftItemCreate(BaseModel):
    title: str
    description: str | None = None
    url: str | None = None
    price_cents: int | None = None

@router.post('/', response_model=dict)
def create_registry(data: RegistryCreate, session: Session = Depends(get_session), user = Depends(get_current_user)):
    reg = Registry(name=data.name, occasion=data.occasion, owner_id=user.id, is_public=data.is_public)
    session.add(reg)
    session.commit()
    session.refresh(reg)
    return {'id': reg.id, 'share_id': reg.share_id}

@router.post('/{registry_id}/items', response_model=GiftItemOut)
def add_item(registry_id: int, item: GiftItemCreate, session: Session = Depends(get_session), user = Depends(get_current_user)):
    reg = session.get(Registry, registry_id)
    if not reg or reg.owner_id != user.id:
        raise HTTPException(status_code=403, detail='Forbidden')
    gi = GiftItem(registry_id=registry_id, **item.dict())
    session.add(gi)
    session.commit()
    session.refresh(gi)
    return {'id': gi.id, 'title': gi.title, 'bought': gi.bought}

@router.get("/{share_id}")
def view_registry(share_id: str, session: Session = Depends(get_session)):
    stmt = select(Registry).where(Registry.share_id == share_id)
    reg = session.exec(stmt).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    items = session.exec(select(GiftItem).where(GiftItem.registry_id==reg.id)).all()
    return {"id": reg.id, "name": reg.name, "occasion": reg.occasion, "items": items, "is_public": reg.is_public, "owner_id": reg.owner_id, "share_id": reg.share_id}

@router.post("/items/{item_id}/buy", response_model=GiftItemOut)
def buy_item_endpoint(item_id: int, session: Session = Depends(get_session), user = Depends(get_current_user)):
    # wraps buy_item (which locks the row)
    item = buy_item(item_id, user.id, session)
    return item

@router.post("/items/{item_id}/reserve", response_model=GiftItemOut)
def reserve_item_endpoint(item_id: int, session: Session = Depends(get_session), user = Depends(get_current_user)):
    item = reserve_item(item_id, user.id, session)
    return item

@router.get("/items/search/", response_model=List[GiftItemOut])
def search_items_endpoint(q: str, session: Session = Depends(get_session)):
    items = search_items(q, session)
    return items
