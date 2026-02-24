from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app.models import Cart, CartItem, ProductVariant

def get_or_create_cart(db: Session, user_id: int):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart

def add_to_cart(db: Session, user_id: int, variant_id: int, quantity: int):
    variant = db.query(ProductVariant).filter(
        ProductVariant.variant_id == variant_id
    ).first()

    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    if quantity > variant.stock_qty:
        raise HTTPException(status_code=400, detail="Not enough stock available")

    cart = get_or_create_cart(db, user_id)

    existing = db.query(CartItem).filter(
        CartItem.cart_id == cart.cart_id,
        CartItem.variant_id == variant_id
    ).first()

    if existing:
        existing.quantity += quantity
    else:
        item = CartItem(
            cart_id=cart.cart_id,
            variant_id=variant_id,
            quantity=quantity
        )
        db.add(item)

    db.commit()

    return get_cart_with_items(db, user_id)


def get_cart_with_items(db: Session, user_id: int):
    cart = db.query(Cart).filter(
        Cart.user_id == user_id
    ).options(
        joinedload(Cart.items)
        .joinedload(CartItem.variant)
        .joinedload(ProductVariant.product)
    ).first()

    if not cart:
        cart = get_or_create_cart(db, user_id)

    return cart


def update_cart_item(db: Session, user_id: int, cart_item_id: int, quantity: int):
    item = db.query(CartItem).join(Cart).filter(
        CartItem.cart_item_id == cart_item_id,
        Cart.user_id == user_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if quantity <= 0:
        db.delete(item)
    else:
        item.quantity = quantity

    db.commit()

    return get_cart_with_items(db, user_id)


def remove_cart_item(db: Session, user_id: int, cart_item_id: int):
    item = db.query(CartItem).join(Cart).filter(
        CartItem.cart_item_id == cart_item_id,
        Cart.user_id == user_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()