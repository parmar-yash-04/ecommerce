from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import OrderResponse
from app.core.oauth2 import get_current_user
from app.crud import orders as crud_order

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/my", response_model=list[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return crud_order.get_user_orders(db, user.user_id)

@router.get("/{order_id}", response_model=OrderResponse)
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return crud_order.get_order_by_id(db, order_id, user.user_id)