from fastapi import APIRouter, Depends, HTTPException
from app.schemas.chatbot import ChatRequest, SyncRequest
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.products import Product, ProductVariant
from app.core.config import settings
from app.core.vector_search import (
    get_cohere_client, get_vector_db_connection, ensure_vector_table,
    get_query_embedding, get_embeddings_batch, retrieve_products_from_vector,
    get_product_details, detect_product_intent, sync_all_products_to_vector
)
from groq import Groq

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

def get_groq_client():
    if not settings.GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not configured."
        )
    return Groq(api_key=settings.GROQ_API_KEY)

@router.post("/sync-products")
def sync_products_to_vector(db: Session = Depends(get_db)):
    result = sync_all_products_to_vector(db)
    return result

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

    response = get_groq_client().chat.completions.create(
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
    for row in raw_results:
        variant_id = row[0]
        content = row[1]
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
