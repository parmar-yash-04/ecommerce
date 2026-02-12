from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cart, CartItem, ProductVariant
from app.schemas import CartAddRequest, CartResponse, CartItemResponse, CartUpdateRequest
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

@router.post("/add", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    data: CartAddRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    variant = db.query(ProductVariant).filter(
        ProductVariant.variant_id == data.variant_id
    ).first()

    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

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

@router.get("/", response_model=CartResponse)
def view_cart(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    cart = get_or_create_cart(db, user.user_id)
    return cart

@router.put("/update", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def update_quantity(
    data: CartUpdateRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    item = db.query(CartItem).filter(
        CartItem.cart_item_id == data.cart_item_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if data.quantity <= 0:
        db.delete(item)
    else:
        item.quantity = data.quantity

    db.commit()

    cart = db.query(Cart).filter(
        Cart.cart_id == item.cart_id
    ).first()

    return cart

@router.delete("/remove/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    item = db.query(CartItem).filter(
        CartItem.cart_item_id == cart_item_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()

    return {"message": "Item removed"}