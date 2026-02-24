from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import ProductCreate, ProductResponse, VariantCreate, VariantResponse, ProductWithVariants
from app.core.oauth2 import get_current_user
from app.crud import products as crud_product

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return crud_product.create_product(db, data)

@router.get("/")
def list_products(
    page: int = Query(1, ge=1),
    size: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    return crud_product.list_products(db, page, size)

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return crud_product.get_product_by_id(db, product_id)

@router.post("/variants", response_model=VariantResponse, status_code=status.HTTP_201_CREATED)
def create_variant(
    data: VariantCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return crud_product.create_variant(db, data)

@router.get("/{product_id}/variants", response_model=ProductWithVariants)
def get_product_with_variants(
    product_id: int,
    db: Session = Depends(get_db)
):
    return crud_product.get_product_with_variants(db, product_id)

@router.put("/update/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return crud_product.update_product(db, product_id, data)