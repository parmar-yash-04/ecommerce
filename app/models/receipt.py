from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from datetime import datetime
from app.db.database import Base

class Receipt(Base):
    __tablename__ = "receipts"

    receipt_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"))
    invoice_number = Column(String, unique=True)
    pdf_url = Column(String)
    generated_at = Column(TIMESTAMP, default=datetime.utcnow)