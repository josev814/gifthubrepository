from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..schemas import UserCreate, Token
from ..database import get_session
from ..crud import create_user, authenticate_user
from ..auth import create_access_token

router = APIRouter(prefix="/api")

@router.post("/register")
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(__import__("..models", fromlist=["User"]).User).where(__import__("..models", fromlist=["User"]).User.email == user_in.email)).first()
    if existing:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(user_in.email, user_in.password, session)
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

from fastapi.security import OAuth2PasswordRequestForm
@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
