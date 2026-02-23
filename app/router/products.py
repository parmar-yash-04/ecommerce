from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ProductCreate, ProductResponse, VariantCreate, VariantResponse, ProductWithVariants
from app.models import Product, ProductVariant, Tag
from app.oauth2 import get_current_user
from typing import List

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    product = Product(
    brand=data.brand,
    model_name=data.model_name,
    description=data.description,
    base_price=data.base_price,
    image_url=data.image_url,
    is_active=data.is_active
)
    if data.tag_ids:
        tags = db.query(Tag).filter(Tag.tag_id.in_(data.tag_ids)).all()
        product.tags = tags
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/")
def list_products(
    page: int = Query(1, ge=1),
    size: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * size
    query = db.query(Product).filter(Product.is_active == True)
    total_products = query.count()
    total_pages = (total_products + size - 1) // size
    products = query.offset(offset).limit(size).all()

    return {
        "total": total_products,
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "data": products
    }

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/variants", response_model=VariantResponse, status_code=status.HTTP_201_CREATED)
def create_variant(
    data: VariantCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.product_id == data.product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = db.query(ProductVariant).filter(
    ProductVariant.sku_code == data.sku_code).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="sku_code already exists"
        )

    variant = ProductVariant(**data.model_dump())

    db.add(variant)
    db.commit()
    db.refresh(variant)

    return variant

@router.get("/{product_id}/variants", response_model=ProductWithVariants)
def get_product_with_variants(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product