from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import Tag, products

def get_all_tags(db: Session):
    return db.query(Tag).all()

def create_tag(db: Session, tag_name: str):
    # Check for duplicate
    existing = db.query(Tag).filter(Tag.name == tag_name).first()
    if existing:
        return None  # Return None to indicate duplicate
    
    try:
        tag = Tag(name=tag_name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag
    except IntegrityError:
        db.rollback()
        return None

def get_products_by_tag(db: Session, tag_id: int):
    tag = db.query(Tag).filter(Tag.tag_id == tag_id).first()
    if not tag:
        return []
    return tag.products