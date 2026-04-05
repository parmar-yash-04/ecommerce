from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chatbot import ChatRequest, SyncRequest
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.models.products import Product, ProductVariant
import psycopg2
import numpy as np
import cohere
from app.core.config import settings
from groq import Groq
import re

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

cohere_client = cohere.Client(settings.COHERE_API_KEY)
groq_client = Groq(api_key=settings.GROQ_API_KEY)

VECTOR_DB_CONFIG = {
    "host": "localhost",
    "database": "ragdb",
    "user": "postgres",
    "password": "99240",
    "port": 5432
}

def get_vector_db_connection():
    return psycopg2.connect(**VECTOR_DB_CONFIG)

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

def get_embeddings_batch(texts):
    response = cohere_client.embed(
        texts=texts,
        model="embed-english-v3.0",
        input_type="search_document"
    )
    return [np.array(e) for e in list(response.embeddings)]

def get_query_embedding(text):
    response = cohere_client.embed(
        texts=[text],
        model="embed-english-v3.0",
        input_type="search_query"
    )
    return np.array(list(response.embeddings)[0])

@router.post("/sync-products")
def sync_products_to_vector(db: Session = Depends(get_db)):
    ensure_vector_table()

    products = db.query(Product).filter(Product.is_active == True).all()

    product_texts = []
    variant_ids = []

    for product in products:
        for variant in product.variants:
            text = (
                f"Product: {product.brand} {product.model_name}. "
                f"Price: ₹{variant.price}. Color: {variant.color}. "
                f"RAM: {variant.ram}. Storage: {variant.storage}. "
                f"Description: {product.description}"
            )
            product_texts.append(text)
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

def retrieve_products_from_vector(query_embedding, top_k=50):
    conn = get_vector_db_connection()
    cur = conn.cursor()
    embedding_str = "[" + ",".join(map(str, query_embedding.tolist())) + "]"
    cur.execute(
        """
        SELECT variant_id, content FROM product_documents
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (embedding_str, top_k)
    )
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def detect_product_intent(message):
    message_lower = message.lower()

    budget = None
    budget_type = None
    brands = []

    brand_keywords = [
        'samsung', 'apple', 'iphone', 'oneplus', 'redmi', 'xiaomi',
        'realme', 'oppo', 'vivo', 'moto', 'motorola', 'asus', 'nothing', 'poco'
    ]

    for brand in brand_keywords:
        if brand in message_lower:
            brands.append(brand.title())

    price_between_match = re.search(
        r'between\s*(\d+(?:,\d{3})*)\s*(?:and|to|-)\s*(\d+(?:,\d{3})*)', message_lower
    )
    if price_between_match:
        budget = (
            int(price_between_match.group(1).replace(',', '')),
            int(price_between_match.group(2).replace(',', ''))
        )
        budget_type = 'between'

    if not budget:
        price_under_match = re.search(
            r'(?:under|below|less than|within|budget[:\s]+)\s*(\d+(?:,\d{3})*(?:\.\d+)?)', message_lower
        )
        if price_under_match:
            budget = int(float(price_under_match.group(1).replace(',', '')))
            budget_type = 'under'

    if not budget:
        price_above_match = re.search(
            r'(?:above|over|more than|greater than)\s*(\d+(?:,\d{3})*(?:\.\d+)?)', message_lower
        )
        if price_above_match:
            budget = int(float(price_above_match.group(1).replace(',', '')))
            budget_type = 'above'

    if not budget:
        price_k_match = re.search(r'(\d+)\s*k\b', message_lower)
        if price_k_match:
            budget = int(price_k_match.group(1)) * 1000
            budget_type = 'under'

    return {
        'budget': budget,
        'budget_type': budget_type,
        'brands': brands,
        'raw_query': message
    }

def get_product_details(variant_id: int, db: Session):
    variant = db.query(ProductVariant).filter(ProductVariant.variant_id == variant_id).first()
    if not variant:
        return None

    product = db.query(Product).filter(Product.product_id == variant.product_id).first()
    if not product:
        return None

    return {
        'product_id': product.product_id,
        'variant_id': variant.variant_id,
        'brand': product.brand,
        'model_name': product.model_name,
        'color': variant.color,
        'ram': variant.ram,
        'storage': variant.storage,
        'price': variant.price,
        'image_url': variant.image_url or product.image_url,
        'description': product.description
    }

def answer_product_question(question, products_data, intent):
    product_list = "\n\n".join([
        f"- {p['brand']} {p['model_name']} - ₹{p['price']} - {p['ram']} RAM - "
        f"{p['storage']} Storage - Color: {p['color']} (ID: {p['variant_id']})"
        for p in products_data
    ])

    price_filter_instruction = ""
    if intent.get('budget'):
        budget_val = intent.get('budget')
        budget_type = intent.get('budget_type')
        if budget_type == 'between' and isinstance(budget_val, tuple):
            min_price, max_price = budget_val
            price_filter_instruction = f"\nIMPORTANT: Only show products with price between ₹{min_price:,} and ₹{max_price:,}."
        elif budget_type == 'under':
            price_filter_instruction = f"\nIMPORTANT: Only show products with price UNDER ₹{budget_val:,}."
        elif budget_type == 'above':
            price_filter_instruction = f"\nIMPORTANT: Only show products with price ABOVE ₹{budget_val:,}."

    prompt = f"""You are a helpful e-commerce shopping assistant. Based on the product database, recommend products to the user.

Available Products:
{product_list}

User Question: {question}
{price_filter_instruction}

Instructions:
- Recommend ONLY from the available products listed above
- Filter by price if the user specifies a budget
- Present recommendations in a friendly, helpful manner, using space between each product for clarity
- Include product details (brand, model, price, specs)
- Format your response clearly with bullet points using "•" or "-" (Not asterisks "*") 
- If no products match the budget, say so politely and suggest the closest alternatives
- After each product, add a view button in this format: [VIEW_PRODUCT:variant_id]
"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1024
    )
    return response.choices[0].message.content

@router.post("/chat")
def chat_with_products(request: ChatRequest, db: Session = Depends(get_db)):
    ensure_vector_table()

    question = request.message
    intent = detect_product_intent(question)
    query_embedding = get_query_embedding(question)
    raw_results = retrieve_products_from_vector(query_embedding, top_k=50)

    if not raw_results:
        return {
            "answer": "I couldn't find any products in our database.",
            "products": []
        }

    product_data = []
    for variant_id, content in raw_results:
        details = get_product_details(variant_id, db)
        if details:
            details['content'] = content
            product_data.append(details)

    if not product_data:
        return {
            "answer": "No products found.",
            "products": []
        }

    filtered_products = product_data.copy()

    if intent.get('budget'):
        budget_val = intent['budget']
        budget_type = intent.get('budget_type', 'under')

        if budget_type == 'under' and isinstance(budget_val, int):
            filtered_products = [p for p in product_data if p['price'] <= budget_val]
        elif budget_type == 'above' and isinstance(budget_val, int):
            filtered_products = [p for p in product_data if p['price'] >= budget_val]
        elif budget_type == 'between' and isinstance(budget_val, tuple):
            min_price, max_price = budget_val
            filtered_products = [p for p in product_data if min_price <= p['price'] <= max_price]

    if intent.get('brands'):
        brand_list = [b.lower() for b in intent['brands']]
        filtered_products = [p for p in filtered_products if any(b in p['brand'].lower() for b in brand_list)]

    if not filtered_products and intent.get('budget') and isinstance(intent['budget'], int):
        expanded_budget = int(intent['budget'] * 1.2)
        filtered_products = [p for p in product_data if p['price'] <= expanded_budget]

    if not filtered_products:
        filtered_products = product_data[:10]

    answer = answer_product_question(question, filtered_products, intent)

    return {
        "answer": answer,
        "products": filtered_products[:10],
        "intent": intent
    }

@router.get("/status")
def chatbot_status():
    ensure_vector_table()

    conn = get_vector_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM product_documents;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()

    return {
        "status": "active",
        "products_indexed": count
    }