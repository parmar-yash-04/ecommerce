from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from datetime import datetime
from app.db.database import Base

class RecentlyViewed(Base):
    __tablename__ = "recently_viewed"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    viewed_at = Column(TIMESTAMP, default=datetime.utcnow)