import random
import traceback
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import OTPVerification
from app.schemas import OTPSendRequest, OTPVerifyRequest
from app.utils import send_email
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
        expires_at=datetime.utcnow() + timedelta(minutes=2)
    )

    db.add(record)
    db.commit()

    try:
        send_email(data.email, otp)
    except Exception as e:
        print(f"Failed to send email: {e}")
        print(traceback.format_exc())

    return {
        "message": "OTP sent to your email"
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