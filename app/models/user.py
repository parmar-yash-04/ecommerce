from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String, name="user_name", index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    hashed_password = Column(String)
    google_id = Column(String, unique=True, nullable=True)
    is_verified = Column(Boolean, default=True)
    create_at = Column(TIMESTAMP, default=datetime.utcnow)
    orders = relationship("Order", back_populates="user")