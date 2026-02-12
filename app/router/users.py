from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, Token, login
from app.utils import hash_password
from app import oauth2

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/create", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    hashed_password = hash_password(user.password)
    new_user = User(
        email=user.email,
        username=user.username,
        phone_number=user.phone_number,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(user_credentials: login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid Credentials")
    
    if not hash_password(user_credentials.password) == user.hashed_password:
        raise HTTPException(status_code=403, detail="Invalid Credentials")
    
    access_token = oauth2.create_access_token(data={"user_id": user.user_id})
    
    return {"access_token": access_token, "token_type": "bearer"}