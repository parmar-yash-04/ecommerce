from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cart, CartItem, ProductVariant
from app.schemas import CartAddRequest, CartResponse, CartItemResponse
from app.oauth2 import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])

def get_or_create_cart(db: Session, user_id: int):
    cart = db.query(Cart).filter(
        Cart.user_id == user_id
    ).first()

    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart
    
@router.post("/add", response_model=CartResponse)
def add_to_cart(
    data: CartAddRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    variant = db.query(ProductVariant).filter(
        ProductVariant.variant_id == data.variant_id
    ).first()

    if not variant:
        raise HTTPException(404, "Variant not found")

    cart = get_or_create_cart(db, user.user_id)

    existing = db.query(CartItem).filter(
        CartItem.cart_id == cart.cart_id,
        CartItem.variant_id == data.variant_id
    ).first()

    if existing:
        existing.quantity += data.quantity
    else:
        item = CartItem(
            cart_id=cart.cart_id,
            variant_id=data.variant_id,
            quantity=data.quantity
        )
        db.add(item)

    db.commit()
    db.refresh(cart)
    return cart