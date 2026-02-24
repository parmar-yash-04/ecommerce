from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.products import product_tags

class Tag(Base):
    __tablename__ = "tags"

    tag_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    products = relationship("Product", secondary=product_tags, back_populates="tags")