from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Product, Wishlist, WishlistItem

def get_or_create_wishlist(db: Session, user_id: int):
    wl = db.query(Wishlist).filter(
        Wishlist.user_id == user_id
    ).first()

    if not wl:
        wl = Wishlist(user_id=user_id)
        db.add(wl)
        db.commit()
        db.refresh(wl)

    return wl


def add_to_wishlist(db: Session, user_id: int, product_id: int):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    wl = get_or_create_wishlist(db, user_id)

    exists = db.query(WishlistItem).filter(
        WishlistItem.wishlist_id == wl.wishlist_id,
        WishlistItem.product_id == product_id
    ).first()

    if not exists:
        db.add(WishlistItem(
            wishlist_id=wl.wishlist_id,
            product_id=product_id
        ))
        db.commit()

    db.refresh(wl)
    return wl


def get_wishlist(db: Session, user_id: int):
    return get_or_create_wishlist(db, user_id)


def remove_from_wishlist(db: Session, user_id: int, wishlist_item_id: int):
    item = db.query(WishlistItem).join(Wishlist).filter(
        WishlistItem.wishlist_item_id == wishlist_item_id,
        Wishlist.user_id == user_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()