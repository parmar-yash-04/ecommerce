import random
from fastapi import HTTPException
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import OTPVerification

def create_otp_record(db: Session, email: str):
    otp = str(random.randint(100000, 999999))

    record = OTPVerification(
        email=email,
        otp_code=otp,
        expires_at=datetime.utcnow() + timedelta(minutes=2),
        is_used=False
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return otp

def verify_otp_record(db: Session, email: str, otp: str):
    record = db.query(OTPVerification).filter(
        OTPVerification.email == email,
        OTPVerification.otp_code == otp,
        OTPVerification.is_used == False
    ).order_by(OTPVerification.created_at.desc()).first()

    if not record:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    record.is_used = True
    db.commit()

    return True