from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.oauth2 import create_access_token
from app.utils import verify_password
from app.schemas import Token

router = APIRouter(tags=["Authentication"])

@router.post("/auth/login", response_model=Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid Credentials")
    
    if not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=403, detail="Invalid Credentials")
    
    access_token = create_access_token(data={"user_id": user.user_id})
    
    return {"access_token": access_token, "token_type": "bearer"}