from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, WishlistItem, Wishlist
from app.schemas import WishlistAddRequest, WishlistResponse
from app.oauth2 import get_current_user

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])

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

@router.post("/add", response_model=WishlistResponse)
def add_to_wishlist(
    data: WishlistAddRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.product_id == data.product_id
    ).first()

    if not product:
        raise HTTPException(404, "Product not found")

    wl = get_or_create_wishlist(db, user.user_id)

    exists = db.query(WishlistItem).filter(
        WishlistItem.wishlist_id == wl.wishlist_id,
        WishlistItem.product_id == data.product_id
    ).first()

    if not exists:
        db.add(WishlistItem(
            wishlist_id=wl.wishlist_id,
            product_id=data.product_id
        ))
        db.commit()

    db.refresh(wl)
    return wl

@router.get("/", response_model=WishlistResponse)
def view_wishlist(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    wl = get_or_create_wishlist(db, user.user_id)
    return wl

@router.delete("/remove/{wishlist_item_id}")
def remove_from_wishlist(
    wishlist_item_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    item = db.query(WishlistItem).filter(
        WishlistItem.wishlist_item_id == wishlist_item_id
    ).first()

    if not item:
        raise HTTPException(404, "Item not found")

    db.delete(item)
    db.commit()

    return {"message": "Removed from wishlist"}