import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import OTPVerification
from app.schemas import OTPSendRequest, OTPVerifyRequest
from datetime import datetime, timedelta

router = APIRouter(prefix="/otp", tags=["OTP"])

@router.post("/send")
def send_otp(
    data: OTPSendRequest,
    db: Session = Depends(get_db)
):
    otp = str(random.randint(100000, 999999))

    record = OTPVerification(
        email=data.email,
        otp_code=otp,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )

    db.add(record)
    db.commit()

    return {
        "message": "OTP generated",
        "otp": otp
    }

@router.post("/verify")
def verify_otp(
    data: OTPVerifyRequest,
    db: Session = Depends(get_db)
):
    record = db.query(OTPVerification).filter(
        OTPVerification.email == data.email,
        OTPVerification.otp_code == data.otp,
        OTPVerification.is_used == False
    ).order_by(OTPVerification.created_at.desc()).first()

    if not record:
        raise HTTPException(400, "Invalid OTP")

    if record.expires_at < datetime.utcnow():
        raise HTTPException(400, "OTP expired")

    record.is_used = True
    db.commit()

    return {"message": "OTP verified"}