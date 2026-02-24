from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    order_number = Column(String, unique=True)
    total_amount = Column(Float)
    order_status = Column(String, default="placed")
    payment_status = Column(String, default="pending")
    shipping_address = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"))
    variant_id = Column(Integer, ForeignKey("product_variants.variant_id"))
    quantity = Column(Integer)
    price_each = Column(Float)
    subtotal = Column(Float)
    order = relationship("Order", back_populates="items")