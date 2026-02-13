from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order, OrderItem
from app.schemas import OrderResponse
from app.oauth2 import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/my", response_model=list[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    orders = db.query(Order).filter(
        Order.user_id == user.user_id
    ).order_by(Order.created_at.desc()).all()

    return orders

@router.get("/{order_id}", response_model=OrderResponse)
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.order_id == order_id,
        Order.user_id == user.user_id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    return order