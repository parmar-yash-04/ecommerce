from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import CheckoutRequest, CheckoutResponse, OrderResponse
from app.core.oauth2 import get_current_user
from app.crud import checkout as crud_checkout

router = APIRouter(prefix="/checkout", tags=["Checkout"])

@router.post("/place-order", response_model=CheckoutResponse)
def place_order(
    data: CheckoutRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    order = crud_checkout.place_order(
        db,
        user.user_id,
        data.email,
        data.otp,
        data.shipping_address
    )

    return {
        "order": order,
        "payment_link_url": None
    }

@router.get("/my-orders", response_model=list[OrderResponse])
def my_orders(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return crud_checkout.get_user_orders(db, user.user_id)