from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import Token, ForgotPasswordRequest, ResetPasswordRequest
from app.crud import auth as crud_auth
from app.crud import otp as crud_otp
from app.crud import users as crud_users
from app.core.utils import verify_password, send_email
from app.core.oauth2 import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud_auth.get_user_by_email(db, user_credentials.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )

    if not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )

    access_token = create_access_token(data={"user_id": user.user_id})

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    user = crud_users.get_user_by_email(db, data.email)
    if user:
        otp = crud_otp.create_otp_record(db, data.email)
        try:
            send_email(data.email, otp)
        except Exception as e:
            print(f"Failed to send email: {e}")
    return {}

@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    crud_otp.verify_otp_record(db, data.email, data.otp)
    crud_users.update_password(db, data.email, data.new_password)
    return {"message": "Password reset successful"}