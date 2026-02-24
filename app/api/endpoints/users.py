from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import UserCreate, UserResponse, login, Token
from app.crud import users as crud_user
from app.core.utils import hash_password
from app.core import oauth2

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return crud_user.create_user(db, user)

@router.post("/login", response_model=Token)
def login(user_credentials: login, db: Session = Depends(get_db)):
    user = crud_user.get_user_by_email(db, user_credentials.email)

    if not user:
        raise HTTPException(status_code=403, detail="Invalid Credentials")

    if user.hashed_password != hash_password(user_credentials.password):
        raise HTTPException(status_code=403, detail="Invalid Credentials")

    access_token = oauth2.create_access_token(data={"user_id": user.user_id})

    return {"access_token": access_token, "token_type": "bearer"}