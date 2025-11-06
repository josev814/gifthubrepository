import os
import secrets

from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..auth import get_current_user
from ..database import get_session, get_redis


router = APIRouter(prefix='/api', tags=['csrf'])

@router.get('/csrf-token')
def csrf_token(user = Depends(get_current_user)):
    token = secrets.token_urlsafe(32)
    r = get_redis()
    r.setex(f'csrf:{token}', 300, str(user.id))
    return {'csrf_token': token}
