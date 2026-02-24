from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas.order import OrderResponse

class CheckoutRequest(BaseModel):
    email: EmailStr
    otp: str
    shipping_address: str

class CheckoutResponse(BaseModel):
    order: OrderResponse
    payment_link_url: Optional[str] = None

    class Config:
        from_attributes = True