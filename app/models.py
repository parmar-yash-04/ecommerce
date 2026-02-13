from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, Float
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String, name="user_name", index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    hashed_password = Column(String)
    is_verified = Column(Boolean, default=True)
    create_at = Column(TIMESTAMP, default=datetime.utcnow)
    carts = relationship("Cart", back_populates="user")
    wishlist = relationship("Wishlist", back_populates="user")
    orders = relationship("Order", back_populates="user")

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
    product = relationship("Product", back_populates="variants")

class Cart(Base):
    __tablename__ = "carts"

    cart_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    user = relationship("User", back_populates="carts")
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

class Wishlist(Base):
    __tablename__ = "wishlists"

    wishlist_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    user = relationship("User", back_populates="wishlist")
    items = relationship("WishlistItem", back_populates="wishlist")

class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    wishlist_item_id = Column(Integer, primary_key=True)
    wishlist_id = Column(Integer, ForeignKey("wishlists.wishlist_id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    added_at = Column(TIMESTAMP, default=datetime.utcnow)
    wishlist = relationship("Wishlist", back_populates="items")
    product = relationship("Product")

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

class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    otp_id = Column(Integer, primary_key=True)
    email = Column(String, index=True)
    otp_code = Column(String)
    expires_at = Column(TIMESTAMP)
    is_used = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class Receipt(Base):
    __tablename__ = "receipts"

    receipt_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"))
    invoice_number = Column(String, unique=True)
    pdf_url = Column(String)
    generated_at = Column(TIMESTAMP, default=datetime.utcnow)