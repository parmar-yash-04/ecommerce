from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.oauth2 import get_current_user
from app.crud import recentview as crud_recent

router = APIRouter(prefix="/recently-viewed", tags=["Recently Viewed"])

@router.post("/add/{product_id}")
def add_recently_viewed(
    product_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    crud_recent.add_recently_viewed(
        db,
        user.user_id,
        product_id
    )
    return {"message": "Product added to recently viewed"}

@router.get("/")
def get_recently_viewed(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return crud_recent.get_recently_viewed(
        db,
        user.user_id
    )