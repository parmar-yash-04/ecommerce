from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
from app.models import Product, ProductVariant, Tag
from app.core.vector_search import (
    get_query_embedding,
    retrieve_products_from_vector,
    get_product_details,
    ensure_vector_table,
    detect_product_intent,
    sync_all_products_to_vector,
    product_variant_to_dict,
    product_matches_required_intent,
    score_product_match,
    normalize_search_text,
)

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

    try:
        sync_all_products_to_vector(db)
    except Exception:
        pass

    return product


def search_products(db: Session, query: str, page: int, size: int):
    ensure_vector_table()

    intent = detect_product_intent(query)
    vector_distances = {}
    try:
        query_embedding = get_query_embedding(query)
        raw_results = retrieve_products_from_vector(query_embedding, top_k=100, score_threshold=1.4)
        vector_distances = {row[0]: row[2] for row in raw_results}
    except Exception:
        vector_distances = {}

    variants = (
        db.query(ProductVariant)
        .join(Product)
        .filter(Product.is_active == True)
        .all()
    )

    ranked_results = []
    for variant in variants:
        product = variant.product
        details = product_variant_to_dict(product, variant)
        if not product_matches_required_intent(details, intent):
            continue

        distance = vector_distances.get(variant.variant_id)
        score = score_product_match(details, intent, distance)
        if score <= 0 and variant.variant_id not in vector_distances:
            continue

        ranked_results.append((score, distance if distance is not None else 999, details))

    if not ranked_results and intent.get("budget_type") == "under" and isinstance(intent.get("budget"), int):
        relaxed_intent = dict(intent)
        relaxed_intent["budget"] = int(intent["budget"] * 1.5)

        for variant in variants:
            product = variant.product
            details = product_variant_to_dict(product, variant)
            if not product_matches_required_intent(details, relaxed_intent):
                continue

            distance = vector_distances.get(variant.variant_id)
            score = score_product_match(details, relaxed_intent, distance) + 1
            ranked_results.append((score, distance if distance is not None else 999, details))

    ranked_results.sort(key=lambda item: (-item[0], item[1], item[2]["price"] or 0))

    seen = {}
    for score, distance, details in ranked_results:
        pid = details["product_id"]
        if pid not in seen:
            seen[pid] = details

    all_results = list(seen.values())
    total = len(all_results)
    total_pages = (total + size - 1) // size
    offset = (page - 1) * size
    paginated = all_results[offset:offset + size]

    return {
        "total": total,
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "query": query,
        "data": paginated
    }


def _add_suggestion(suggestions, seen, text, suggestion_type, score):
    normalized = normalize_search_text(text)
    if not normalized or normalized in seen:
        return

    seen.add(normalized)
    suggestions.append({
        "text": text,
        "type": suggestion_type,
        "score": score
    })


def get_search_suggestions(db: Session, query: str, limit: int):
    query_text = normalize_search_text(query)
    suggestions = []
    seen = set()

    if not query_text:
        popular = (
            db.query(Product)
            .filter(Product.is_active == True)
            .order_by(Product.created_at.desc())
            .limit(limit)
            .all()
        )
        for product in popular:
            _add_suggestion(
                suggestions,
                seen,
                f"{product.brand} {product.model_name}",
                "product",
                80
            )
        return {"query": query, "suggestions": suggestions[:limit]}

    products = (
        db.query(Product)
        .filter(
            Product.is_active == True,
            or_(
                Product.brand.ilike(f"%{query_text}%"),
                Product.model_name.ilike(f"%{query_text}%"),
                Product.description.ilike(f"%{query_text}%")
            )
        )
        .limit(25)
        .all()
    )

    for product in products:
        brand = product.brand or ""
        model_name = product.model_name or ""
        product_text = normalize_search_text(f"{brand} {model_name}")
        brand_text = normalize_search_text(brand)

        if product_text.startswith(query_text):
            score = 100
        elif brand_text.startswith(query_text):
            score = 95
        else:
            score = 75

        _add_suggestion(suggestions, seen, f"{brand} {model_name}", "product", score)
        _add_suggestion(suggestions, seen, f"{brand} phone", "brand", score - 5)

    variants = (
        db.query(ProductVariant)
        .join(Product)
        .filter(Product.is_active == True)
        .limit(100)
        .all()
    )

    for variant in variants:
        ram = str(variant.ram or "").strip()
        storage = str(variant.storage or "").strip()
        color = str(variant.color or "").strip()
        price = int(variant.price or 0)

        candidates = []
        if ram:
            candidates.append((f"{ram}GB RAM phone", "spec"))
        if storage:
            candidates.append((f"{storage}GB storage phone", "spec"))
        if color:
            candidates.append((f"{color} phone", "color"))

        for text, suggestion_type in candidates:
            normalized = normalize_search_text(text)
            if normalized.startswith(query_text):
                _add_suggestion(suggestions, seen, text, suggestion_type, 90)
            elif query_text in normalized:
                _add_suggestion(suggestions, seen, text, suggestion_type, 70)

    feature_suggestions = [
        "gaming phone",
        "best camera phone",
        "5G mobile",
        "battery phone",
        "phone under 10k",
        "phone under 15k",
        "phone under 20k",
        "phone under 30k",
        "phone above 50k",
        "phone under 10000",
        "phone under 15000",
        "phone under 20000",
        "phone under 30000",
        "phone above 50000",
    ]
    for text in feature_suggestions:
        normalized = normalize_search_text(text)
        if normalized.startswith(query_text):
            _add_suggestion(suggestions, seen, text, "query", 95)
        elif query_text in normalized:
            _add_suggestion(suggestions, seen, text, "query", 72)

    suggestions.sort(key=lambda item: (-item["score"], item["text"]))

    return {
        "query": query,
        "suggestions": suggestions[:limit]
    }

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

    try:
        sync_all_products_to_vector(db)
    except Exception:
        pass

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

    try:
        sync_all_products_to_vector(db)
    except Exception:
        pass

    return product
