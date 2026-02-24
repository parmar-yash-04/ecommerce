from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Product, ProductVariant, Tag

def create_product(db: Session, data):
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

def list_products(db: Session, page: int, size: int):
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


def get_product_by_id(db: Session, product_id: int):
    product = db.query(Product).filter(
        Product.product_id == product_id,
        Product.is_active == True
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


def create_variant(db: Session, data):
    product = db.query(Product).filter(
        Product.product_id == data.product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = db.query(ProductVariant).filter(
        ProductVariant.sku_code == data.sku_code
    ).first()

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


def get_product_with_variants(db: Session, product_id: int):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

def update_product(db: Session, product_id: int, data):
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    if data.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.tag_id.in_(data.tag_ids)).all()
        product.tags = tags

    db.commit()
    db.refresh(product)

    return product