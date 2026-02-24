from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas import TagCreate, TagResponse
from app.models.tag import Tag
from app.crud import tag as crud_tag

router = APIRouter(prefix="/tags", tags=["Tags"])

@router.get("/tags", response_model=List[TagResponse])
def list_tags(db: Session = Depends(get_db)):
    return crud_tag.get_all_tags(db)

@router.post("/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    new_tag = crud_tag.create_tag(db, tag.name)
    if new_tag is None:
        raise HTTPException(status_code=400, detail="Tag already exists")
    return new_tag

@router.get("/tags/{tag_id}/products")
def products_by_tag(tag_id: int, db: Session = Depends(get_db)):
    return crud_tag.get_products_by_tag(db, tag_id)