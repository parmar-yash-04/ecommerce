from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.sqltypes import TIMESTAMP
from datetime import datetime
from app.db.database import Base

class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    otp_id = Column(Integer, primary_key=True)
    email = Column(String, index=True)
    otp_code = Column(String)
    expires_at = Column(TIMESTAMP)
    is_used = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)