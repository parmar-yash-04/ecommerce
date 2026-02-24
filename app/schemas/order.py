from pydantic import BaseModel
from typing import List
from datetime import datetime

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