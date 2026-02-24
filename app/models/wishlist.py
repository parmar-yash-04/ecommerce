from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Wishlist(Base):
    __tablename__ = "wishlists"

    wishlist_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    items = relationship("WishlistItem", back_populates="wishlist")

class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    wishlist_item_id = Column(Integer, primary_key=True)
    wishlist_id = Column(Integer, ForeignKey("wishlists.wishlist_id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    added_at = Column(TIMESTAMP, default=datetime.utcnow)
    wishlist = relationship("Wishlist", back_populates="items")
    product = relationship("Product")