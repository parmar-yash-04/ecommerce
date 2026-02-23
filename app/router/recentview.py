from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import RecentlyViewed
from app.oauth2 import get_current_user
from datetime import datetime

router = APIRouter(prefix="/recently-viewed", tags=["Recently Viewed"])

@router.post("/add/{product_id}")
def add_recently_viewed(
    product_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    existing_entry = db.query(RecentlyViewed).filter(
        RecentlyViewed.user_id == user.user_id,
        RecentlyViewed.product_id == product_id
    ).first()

    if existing_entry:
        existing_entry.viewed_at = datetime.utcnow()
    else:
        new_entry = RecentlyViewed(
            user_id=user.user_id,
            product_id=product_id
        )
        db.add(new_entry)

    db.commit()

    recent = db.query(RecentlyViewed).filter(
        RecentlyViewed.user_id == user.user_id
    ).order_by(RecentlyViewed.viewed_at.desc()).all()

    if len(recent) > 5:
        for item in recent[5:]:
            db.delete(item)
        db.commit()
    return {"message": "Product added to recently viewed"}

@router.get("/")
def get_recently_viewed(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    recent_views = db.query(RecentlyViewed).filter(
        RecentlyViewed.user_id == user.user_id
    ).order_by(RecentlyViewed.viewed_at.desc()).limit(7).all()

    return recent_views