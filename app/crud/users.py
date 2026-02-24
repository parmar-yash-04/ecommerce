from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import User
from app.core.utils import hash_password

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_data):
    existing_user = get_user_by_email(db, user_data.email)
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_pw = hash_password(user_data.password)

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        phone_number=user_data.phone_number,
        hashed_password=hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user