import traceback
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import OTPSendRequest, OTPVerifyRequest
from app.core.utils import send_email
from app.crud import otp as crud_otp

router = APIRouter(prefix="/otp", tags=["OTP"])

@router.post("/send")
def send_otp(
    data: OTPSendRequest,
    db: Session = Depends(get_db)
):
    otp = crud_otp.create_otp_record(db, data.email)

    try:
        send_email(data.email, otp)
    except Exception as e:
        print(f"Failed to send email: {e}")
        print(traceback.format_exc())

    return {"message": "OTP sent to your email"}

@router.post("/verify")
def verify_otp(
    data: OTPVerifyRequest,
    db: Session = Depends(get_db)
):
    crud_otp.verify_otp_record(db, data.email, data.otp)
    return {"message": "OTP verified"}