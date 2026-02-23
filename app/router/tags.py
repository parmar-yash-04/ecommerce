from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import TagCreate, TagResponse
from app.models import Product, Tag

router = APIRouter(prefix="/tags", tags=["Tags"])

@router.post("/tags", response_model=TagResponse)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    db_tag = Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.get("/tags", response_model=List[TagResponse])
def list_tags(db: Session = Depends(get_db)):
    tags = db.query(Tag).all()
    return tags

@router.get("/tags/{tag_id}/products", response_model=TagResponse)
def get_products_by_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.tag_id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag