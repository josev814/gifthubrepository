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