from sqlalchemy.orm import Session
from datetime import datetime
from app.models import RecentlyViewed

def add_recently_viewed(db: Session, user_id: int, product_id: int):
    existing_entry = db.query(RecentlyViewed).filter(
        RecentlyViewed.user_id == user_id,
        RecentlyViewed.product_id == product_id
    ).first()

    if existing_entry:
        existing_entry.viewed_at = datetime.utcnow()
    else:
        new_entry = RecentlyViewed(
            user_id=user_id,
            product_id=product_id
        )
        db.add(new_entry)

    db.commit()

    # Keep only latest 5
    recent = db.query(RecentlyViewed).filter(
        RecentlyViewed.user_id == user_id
    ).order_by(RecentlyViewed.viewed_at.desc()).all()

    if len(recent) > 5:
        for item in recent[5:]:
            db.delete(item)
        db.commit()

    return True


def get_recently_viewed(db: Session, user_id: int, limit: int = 7):
    return db.query(RecentlyViewed).filter(
        RecentlyViewed.user_id == user_id
    ).order_by(
        RecentlyViewed.viewed_at.desc()
    ).limit(limit).all()