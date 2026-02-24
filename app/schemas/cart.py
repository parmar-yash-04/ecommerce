from pydantic import BaseModel
from typing import List, Optional

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
    price: float
    color: str
    ram: str
    storage: str
    brand: str
    model_name: str
    image_url: Optional[str] = None

    class Config:
        from_attributes = True
    
    @staticmethod
    def from_db(cart_item):
        return {
            "cart_item_id": cart_item.cart_item_id,
            "variant_id": cart_item.variant_id,
            "quantity": cart_item.quantity,
            "price": cart_item.variant.price,
            "color": cart_item.variant.color,
            "ram": cart_item.variant.ram,
            "storage": cart_item.variant.storage,
            "brand": cart_item.variant.product.brand,
            "model_name": cart_item.variant.product.model_name,
            "image_url": cart_item.variant.product.image_url
        }
    
class CartResponse(BaseModel):
    cart_id: int
    items: List[CartItemResponse]

    class Config:
        from_attributes = True