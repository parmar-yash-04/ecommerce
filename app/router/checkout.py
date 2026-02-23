import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cart, CartItem, ProductVariant, Order, OrderItem, Receipt, OTPVerification
from app.schemas import CheckoutRequest, OrderResponse, CheckoutResponse
from app.oauth2 import get_current_user
from app.config import settings

router = APIRouter(prefix="/checkout", tags=["Checkout"])

def verify_otp(db: Session, email: str, otp: str):
    rec = db.query(OTPVerification).filter(
        OTPVerification.email == email,
        OTPVerification.otp_code == otp,
        OTPVerification.is_used == True
    ).order_by(OTPVerification.created_at.desc()).first()

    if not rec:
        return False

    if rec.expires_at < datetime.utcnow():
        return False

    rec.is_used = True
    db.commit()
    return True

@router.post("/place-order", response_model=CheckoutResponse)
def place_order(
    data: CheckoutRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):

    if data.otp:
        if not verify_otp(db, data.email, data.otp):
            raise HTTPException(400, "OTP invalid or expired")

    cart = db.query(Cart).filter(
        Cart.user_id == user.user_id
    ).first()

    if not cart or not cart.items:
        raise HTTPException(400, "Cart is empty")

    order = Order(
        user_id=user.user_id,
        order_number=str(uuid.uuid4())[:8],
        order_status="placed",
        payment_status="pending",
        shipping_address=data.shipping_address,
        total_amount=0
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    total = 0

    for item in cart.items:

        variant = db.query(ProductVariant).filter(
            ProductVariant.variant_id == item.variant_id
        ).first()

        if not variant:
            continue

        if variant.stock_qty < item.quantity:
            raise HTTPException(
                400,
                f"Not enough stock for variant {variant.variant_id}"
            )

        price = variant.price
        subtotal = price * item.quantity

        order_item = OrderItem(
            order_id=order.order_id,
            variant_id=variant.variant_id,
            quantity=item.quantity,
            price_each=price,
            subtotal=subtotal
        )

        variant.stock_qty -= item.quantity

        db.add(order_item)
        total += subtotal

    order.total_amount = total

    db.query(CartItem).filter(
        CartItem.cart_id == cart.cart_id
    ).delete()

    receipt = Receipt(
        order_id=order.order_id,
        invoice_number="INV-" + str(uuid.uuid4())[:6],
        pdf_url=""
    )

    db.add(receipt)
    db.commit()
    db.refresh(order)

    return {
        "order": order,
        "payment_link_url": None
    }

@router.get("/my-orders", response_model=list[OrderResponse])
def my_orders(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return db.query(Order).filter(
        Order.user_id == user.user_id
    ).all()