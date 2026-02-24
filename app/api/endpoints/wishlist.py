from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import WishlistAddRequest, WishlistResponse
from app.core.oauth2 import get_current_user
from app.crud import wishlist as crud_wishlist

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])

@router.post("/add", response_model=WishlistResponse)
def add_to_wishlist(
    data: WishlistAddRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return crud_wishlist.add_to_wishlist(
        db,
        user.user_id,
        data.product_id
    )


@router.get("/", response_model=WishlistResponse)
def view_wishlist(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return crud_wishlist.get_wishlist(db, user.user_id)


@router.delete("/remove/{wishlist_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_wishlist(
    wishlist_item_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    crud_wishlist.remove_from_wishlist(
        db,
        user.user_id,
        wishlist_item_id
    )