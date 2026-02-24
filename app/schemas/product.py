from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProductCreate(BaseModel):
    brand: str
    model_name: str
    description: Optional[str] = None
    base_price: float
    image_url: Optional[str] = None
    is_active: bool = True
    tag_ids: List[int] = []

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
    image_url: Optional[str] = None

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