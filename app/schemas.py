from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    phone_number: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    phone_number: str
    is_verified: bool

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    brand: str
    model_name: str
    description: Optional[str] = None
    base_price: float
    image_url: Optional[str] = None
    is_active: bool = True

class ProductResponse(BaseModel):
    product_id: int
    brand: str
    model_name: str
    description: Optional[str] = None
    base_price: float
    image_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True
    
class VariantBase(BaseModel):
    color: str
    ram: str
    storage: str
    price: float
    stock_qty: int
    sku_code: str

class VariantCreate(VariantBase):
    product_id: int

class VariantResponse(VariantBase):
    variant_id: int
    product_id: int

    class Config:
        from_attributes = True

class ProductWithVariants(BaseModel):
    model_name: str
    variants: List[VariantResponse]

    class Config:
        from_attributes = True

class CartAddRequest(BaseModel):
    variant_id: int
    quantity: int = 1

class CartUpdateRequest(BaseModel):
    cart_item_id: int
    quantity: int

class CartItemResponse(BaseModel):
    cart_item_id: int
    variant_id: int
    quantity: int

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    cart_id: int
    items: List[CartItemResponse]

    class Config:
        from_attributes = True

class WishlistAddRequest(BaseModel):
    product_id: int

class WishlistItemResponse(BaseModel):
    wishlist_item_id: int
    product_id: int

    class Config:
        from_attributes = True

class WishlistResponse(BaseModel):
    wishlist_id: int
    items: List[WishlistItemResponse]

    class Config:
        from_attributes = True

class OTPSendRequest(BaseModel):
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class CheckoutRequest(BaseModel):
    email: EmailStr
    otp: str
    shipping_address: str

class OrderItemResponse(BaseModel):
    variant_id: int
    quantity: int
    price_each: float
    subtotal: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    order_id: int
    order_number: str
    total_amount: float
    order_status: str
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True

class login(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str