from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import CartAddRequest, CartResponse, CartItemResponse, CartUpdateRequest
from app.core.oauth2 import get_current_user
from app.crud import cart as crud_cart

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/add", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    data: CartAddRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    cart = crud_cart.add_to_cart(db, user.user_id, data.variant_id, data.quantity)

    return {
        "cart_id": cart.cart_id,
        "items": [CartItemResponse.from_db(item) for item in cart.items]
    }

@router.get("/", response_model=CartResponse)
def view_cart(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    cart = crud_cart.get_cart_with_items(db, user.user_id)

    return {
        "cart_id": cart.cart_id,
        "items": [CartItemResponse.from_db(item) for item in cart.items]
    }

@router.put("/update", response_model=CartResponse)
def update_quantity(
    data: CartUpdateRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    cart = crud_cart.update_cart_item(
        db,
        user.user_id,
        data.cart_item_id,
        data.quantity
    )

    return {
        "cart_id": cart.cart_id,
        "items": [CartItemResponse.from_db(item) for item in cart.items]
    }

@router.delete("/remove/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    crud_cart.remove_cart_item(db, user.user_id, cart_item_id)