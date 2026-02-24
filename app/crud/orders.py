from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Order

def get_user_orders(db: Session, user_id: int):
    return db.query(Order).filter(
        Order.user_id == user_id
    ).order_by(Order.created_at.desc()).all()

def get_order_by_id(db: Session, order_id: int, user_id: int):
    order = db.query(Order).filter(
        Order.order_id == order_id,
        Order.user_id == user_id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order