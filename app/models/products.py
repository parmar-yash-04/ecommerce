from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
from sqlalchemy import Table

product_tags = Table(
    'product_tags',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.product_id')),
    Column('tag_id', Integer, ForeignKey('tags.tag_id'))
)

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True)
    brand = Column(String)
    model_name = Column(String, index=True)
    description = Column(Text)
    base_price = Column(Float)
    image_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    variants = relationship("ProductVariant", back_populates="product")
    tags = relationship("Tag", secondary=product_tags, back_populates="products")

class ProductVariant(Base):
    __tablename__ = "product_variants"

    variant_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"))
    color = Column(String)
    ram = Column(String)
    storage = Column(String)
    price = Column(Float)
    stock_qty = Column(Integer)
    sku_code = Column(String, unique=True)
    image_url = Column(String)
    product = relationship("Product", back_populates="variants")