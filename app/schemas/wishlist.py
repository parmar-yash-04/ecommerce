from pydantic import BaseModel
from typing import List, Optional

class WishlistAddRequest(BaseModel):
    product_id: int

class WishlistProductInfo(BaseModel):
    product_id: int
    model_name: str
    brand: str
    base_price: float
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class WishlistItemResponse(BaseModel):
    wishlist_item_id: int
    product: WishlistProductInfo

    class Config:
        from_attributes = True

class WishlistResponse(BaseModel):
    wishlist_id: int
    items: List[WishlistItemResponse]

    class Config:
        from_attributes = True