from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.products import Product, ProductVariant
from app.core.config import settings
import psycopg2
import numpy as np
import cohere
import re

STOP_WORDS = {
    "a", "an", "and", "best", "buy", "for", "in", "mobile", "phone", "phones",
    "below", "product", "show", "smartphone", "the", "under", "with"
}

COLOR_KEYWORDS = [
    "black", "white", "blue", "green", "red", "yellow", "pink", "purple",
    "gold", "silver", "gray", "grey", "orange"
]

FEATURE_KEYWORDS = {
    "gaming": ["gaming", "game", "performance", "processor", "snapdragon"],
    "camera": ["camera", "photo", "photography", "portrait", "video"],
    "battery": ["battery", "mah", "charging", "fast charging"],
    "5g": ["5g"],
}

BRAND_ALIASES = {
    "iphone": "Apple",
    "apple": "Apple",
    "samsung": "Samsung",
    "oneplus": "OnePlus",
    "redmi": "Xiaomi",
    "xiaomi": "Xiaomi",
    "realme": "Realme",
    "oppo": "Oppo",
    "vivo": "Vivo",
    "moto": "Motorola",
    "motorola": "Motorola",
    "asus": "Asus",
    "nothing": "Nothing",
    "poco": "Poco",
    "google": "Google",
    "pixel": "Google",
}


def get_cohere_client():
    if not settings.COHERE_API_KEY:
        raise HTTPException(status_code=500, detail="COHERE_API_KEY is not configured.")
    return cohere.Client(settings.COHERE_API_KEY)


def get_vector_db_connection():
    if settings.env == "production":
        prod_url = settings.chatbot_vector_db_prod_url or settings.database_url
        return psycopg2.connect(prod_url)
    return psycopg2.connect(
        host=settings.chatbot_vector_db_local_host,
        database=settings.chatbot_vector_db_local_database,
        user=settings.chatbot_vector_db_local_user,
        password=settings.chatbot_vector_db_local_password,
        port=settings.chatbot_vector_db_local_port,
    )


def ensure_vector_table():
    conn = get_vector_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS product_documents (
            id SERIAL PRIMARY KEY,
            variant_id INTEGER,
            content TEXT,
            embedding vector(1024)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def get_query_embedding(text):
    response = get_cohere_client().embed(
        texts=[text],
        model="embed-english-v3.0",
        input_type="search_query"
    )
    return np.array(list(response.embeddings)[0])


def get_embeddings_batch(texts):
    response = get_cohere_client().embed(
        texts=texts,
        model="embed-english-v3.0",
        input_type="search_document"
    )
    return [np.array(e) for e in list(response.embeddings)]


def normalize_search_text(value):
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def normalize_capacity(value):
    value = normalize_search_text(value).replace(" ", "")
    if re.fullmatch(r"\d+", value):
        return f"{value}gb"
    match = re.search(r"(\d+)(?:gb|g\b|tb)", value)
    if not match:
        return value
    unit = "tb" if "tb" in value else "gb"
    return f"{match.group(1)}{unit}"


def tokenize_query(query):
    return [
        token for token in re.findall(r"[a-z0-9]+", normalize_search_text(query))
        if token not in STOP_WORDS and len(token) > 1
    ]


def parse_price_value(value, suffix=""):
    amount = float(str(value).replace(",", ""))
    if suffix and suffix.lower() == "k":
        amount *= 1000
    return int(amount)


def build_product_document(product, variant):
    tag_names = " ".join(tag.name for tag in getattr(product, "tags", []) if tag.name)
    return (
        f"Brand: {product.brand}. "
        f"Model: {product.model_name}. "
        f"Category: mobile smartphone phone 5g. "
        f"Price: {variant.price}. "
        f"Color: {variant.color}. "
        f"RAM: {variant.ram}. "
        f"Storage: {variant.storage}. "
        f"Tags: {tag_names}. "
        f"Description: {product.description}"
    )


def retrieve_products_from_vector(query_embedding, top_k=50, score_threshold=0.0):
    conn = get_vector_db_connection()
    cur = conn.cursor()
    embedding_str = "[" + ",".join(map(str, query_embedding.tolist())) + "]"
    cur.execute(
        """
        SELECT variant_id, content, embedding <=> %s::vector AS distance
        FROM product_documents
        ORDER BY distance
        LIMIT %s
        """,
        (embedding_str, top_k)
    )
    results = cur.fetchall()
    cur.close()
    conn.close()

    if score_threshold > 0:
        results = [r for r in results if r[2] <= score_threshold]

    return results


def sync_all_products_to_vector(db: Session):
    ensure_vector_table()
    products = db.query(Product).filter(Product.is_active == True).all()
    product_texts = []
    variant_ids = []

    for product in products:
        for variant in product.variants:
            product_texts.append(build_product_document(product, variant))
            variant_ids.append(variant.variant_id)

    if not product_texts:
        return {"message": "No products found", "synced": 0}

    embeddings = get_embeddings_batch(product_texts)
    conn = get_vector_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM product_documents;")
    for text, emb, vid in zip(product_texts, embeddings, variant_ids):
        emb_str = "[" + ",".join(map(str, emb.tolist())) + "]"
        cur.execute(
            "INSERT INTO product_documents (variant_id, content, embedding) VALUES (%s, %s, %s::vector)",
            (vid, text, emb_str)
        )
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Products synced successfully", "synced": len(product_texts)}


def get_product_details(variant_id: int, db: Session):
    variant = db.query(ProductVariant).filter(ProductVariant.variant_id == variant_id).first()
    if not variant:
        return None
    product = db.query(Product).filter(Product.product_id == variant.product_id).first()
    if not product:
        return None
    return product_variant_to_dict(product, variant)


def product_variant_to_dict(product, variant):
    return {
        "product_id": product.product_id,
        "variant_id": variant.variant_id,
        "brand": product.brand,
        "model_name": product.model_name,
        "color": variant.color,
        "ram": variant.ram,
        "storage": variant.storage,
        "price": variant.price,
        "image_url": variant.image_url or product.image_url,
        "description": product.description,
        "tags": [tag.name for tag in getattr(product, "tags", []) if tag.name],
    }


def build_searchable_text(product_data):
    return normalize_search_text(
        " ".join([
            str(product_data.get("brand") or ""),
            str(product_data.get("model_name") or ""),
            str(product_data.get("description") or ""),
            str(product_data.get("color") or ""),
            str(product_data.get("ram") or ""),
            str(product_data.get("storage") or ""),
            " ".join(product_data.get("tags") or []),
        ])
    )


def detect_product_intent(message):
    message_lower = normalize_search_text(message)

    budget = None
    budget_type = None
    brands = []
    ram = None
    storage = None
    colors = []
    keywords = []

    for alias, canonical in BRAND_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", message_lower):
            if canonical not in brands:
                brands.append(canonical)

    ram_match = re.search(r"(\d+)\s*(?:gb|g)\s*ram\b", message_lower)
    if ram_match:
        ram = f"{ram_match.group(1)}gb"

    storage_match = re.search(r"(\d+)\s*(?:gb|g|tb)\s*(?:storage|rom)\b", message_lower)
    if storage_match:
        unit = "tb" if "tb" in storage_match.group(0) else "gb"
        storage = f"{storage_match.group(1)}{unit}"

    for color in COLOR_KEYWORDS:
        if re.search(rf"\b{re.escape(color)}\b", message_lower):
            colors.append("gray" if color == "grey" else color)

    for keyword in FEATURE_KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}\b", message_lower):
            keywords.append(keyword)

    price_between_match = re.search(
        r"between\s*(\d+(?:,\d{3})*)(k)?\s*(?:and|to|-)\s*(\d+(?:,\d{3})*)(k)?", message_lower
    )
    if price_between_match:
        budget = (
            parse_price_value(price_between_match.group(1), price_between_match.group(2)),
            parse_price_value(price_between_match.group(3), price_between_match.group(4))
        )
        budget_type = "between"

    if not budget:
        price_under_match = re.search(
            r"(?:under|below|less than|within|budget[:\s]+)\s*(\d+(?:,\d{3})*(?:\.\d+)?)(k)?", message_lower
        )
        if price_under_match:
            budget = parse_price_value(price_under_match.group(1), price_under_match.group(2))
            budget_type = "under"

    if not budget:
        price_above_match = re.search(
            r"(?:above|over|more than|greater than)\s*(\d+(?:,\d{3})*(?:\.\d+)?)(k)?", message_lower
        )
        if price_above_match:
            budget = parse_price_value(price_above_match.group(1), price_above_match.group(2))
            budget_type = "above"

    if not budget:
        price_k_match = re.search(r"(\d+)\s*k\b", message_lower)
        if price_k_match:
            budget = int(price_k_match.group(1)) * 1000
            budget_type = "under"

    return {
        "budget": budget,
        "budget_type": budget_type,
        "brands": brands,
        "ram": ram,
        "storage": storage,
        "colors": colors,
        "keywords": keywords,
        "query_terms": tokenize_query(message),
        "raw_query": message
    }


def product_matches_required_intent(product, intent):
    brand_list = [b.lower() for b in intent.get("brands") or []]
    if brand_list and not any(b in normalize_search_text(product.get("brand")) for b in brand_list):
        return False

    price = product.get("price") or 0
    budget = intent.get("budget")
    budget_type = intent.get("budget_type")
    if budget:
        if budget_type == "under" and isinstance(budget, int) and price > budget:
            return False
        if budget_type == "above" and isinstance(budget, int) and price < budget:
            return False
        if budget_type == "between" and isinstance(budget, tuple):
            min_price, max_price = budget
            if price < min_price or price > max_price:
                return False

    if intent.get("ram") and normalize_capacity(product.get("ram")) != intent["ram"]:
        return False

    if intent.get("storage") and normalize_capacity(product.get("storage")) != intent["storage"]:
        return False

    colors = intent.get("colors") or []
    product_color = normalize_search_text(product.get("color"))
    if colors and not any(color in product_color for color in colors):
        return False

    keywords = intent.get("keywords") or []
    text = build_searchable_text(product)
    if keywords and not any(keyword in text for keyword in keywords):
        return False

    return True


def score_product_match(product, intent, vector_distance=None):
    text = build_searchable_text(product)
    score = 0.0

    for brand in intent.get("brands") or []:
        if normalize_search_text(brand) in normalize_search_text(product.get("brand")):
            score += 45

    model = normalize_search_text(product.get("model_name"))
    for term in intent.get("query_terms") or []:
        if term in model:
            score += 14
        elif re.search(rf"\b{re.escape(term)}\b", text):
            score += 7

    if intent.get("ram") and normalize_capacity(product.get("ram")) == intent["ram"]:
        score += 25

    if intent.get("storage") and normalize_capacity(product.get("storage")) == intent["storage"]:
        score += 25

    for color in intent.get("colors") or []:
        if color in normalize_search_text(product.get("color")):
            score += 20

    price = product.get("price") or 0
    budget = intent.get("budget")
    budget_type = intent.get("budget_type")
    if budget:
        if budget_type == "under" and isinstance(budget, int) and price <= budget:
            score += 25
        elif budget_type == "above" and isinstance(budget, int) and price >= budget:
            score += 25
        elif budget_type == "between" and isinstance(budget, tuple):
            min_price, max_price = budget
            if min_price <= price <= max_price:
                score += 25

    for keyword in intent.get("keywords") or []:
        related_terms = FEATURE_KEYWORDS.get(keyword, [keyword])
        if any(term in text for term in related_terms):
            score += 30

    if vector_distance is not None:
        score += max(0, 30 - (float(vector_distance) * 25))

    return score
