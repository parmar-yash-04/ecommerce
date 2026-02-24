from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Cart(Base):
    __tablename__ = "carts"

    cart_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    items = relationship("CartItem", back_populates="cart")

class CartItem(Base):
    __tablename__ = "cart_items"

    cart_item_id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("carts.cart_id", ondelete="CASCADE"))
    variant_id = Column(Integer, ForeignKey("product_variants.variant_id", ondelete="CASCADE"))
    quantity = Column(Integer, default=1)
    added_at = Column(TIMESTAMP, default=datetime.utcnow)
    cart = relationship("Cart", back_populates="items")
    variant = relationship("ProductVariant")