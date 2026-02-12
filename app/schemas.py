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

class ProductBase(BaseModel):
    brand: str
    model_name: str
    description: Optional[str] = None
    base_price: float
    image_url: Optional[str] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    product_id: int
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

class ProductWithVariants(ProductResponse):
    variants: List[VariantResponse] = []

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
    added_at: datetime

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    cart_id: int
    items: List[CartItemResponse]

    class Config:
        from_attributes = True

class login(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str