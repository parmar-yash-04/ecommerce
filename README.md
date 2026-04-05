![Phone Shop Banner](https://via.placeholder.com/1200x400/2563eb/ffffff?text=Phone+Shop+API)

<div align="center">

# 📱 Phone Shop - E-Commerce REST API

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-00a856.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-orange.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![API Status](https://img.shields.io/badge/API-Health-00a856.svg)](https://)

</div>

---

## 🚀 About The Project

Phone Shop is a production-ready REST API for a mobile phone e-commerce platform built with **FastAPI**. It provides a complete backend solution for an online phone store with advanced features like AI-powered product recommendations, secure authentication, and modern e-commerce functionality.

### ✨ Key Features

- 🔐 **Secure Authentication** - JWT tokens + Google OAuth 2.0 + OTP verification
- 📦 **Product Management** - Products with multiple variants (colors, RAM, storage)
- 🛒 **Shopping Cart** - Add/remove/update items with quantity management
- ❤️ **Wishlist** - Save favorite products for later
- 📋 **Order Management** - Complete checkout and order tracking
- 🤖 **AI Chatbot** - RAG-powered product search with natural language
- 👁️ **Recently Viewed** - Track user's product browsing history
- 🏷️ **Tags & Categories** - Flexible product organization

---

## 🏗️ Architecture

```
Phone Shop/
├── app/
│   ├── api/              # API endpoints
│   │   └── endpoints/    # Route handlers
│   │       ├── auth.py
│   │       ├── products.py
│   │       ├── cart.py
│   │       ├── wishlist.py
│   │       ├── orders.py
│   │       ├── checkout.py
│   │       ├── chatbot.py
│   │       └── ...
│   ├── core/             # Core utilities
│   │   ├── config.py     # Configuration
│   │   ├── oauth2.py     # JWT handling
│   │   └── utils.py      # Helper functions
│   ├── crud/             # Database operations
│   ├── db/               # Database setup
│   ├── models/           # SQLAlchemy models
│   └── schemas/          # Pydantic schemas
├── alembic/              # Database migrations
├── test/                 # Test suite
└── main.py               # Application entry point
```

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | FastAPI |
| **Language** | Python 3.12 |
| **Database** | PostgreSQL + SQLAlchemy |
| **ORM** | SQLAlchemy 2.0 |
| **Authentication** | JWT, Google OAuth 2.0, OTP |
| **AI/ML** | Cohere Embeddings, Groq LLM |
| **Vector DB** | PostgreSQL with pgvector |
| **Migrations** | Alembic |
| **Testing** | pytest |
| **Deployment** | Render, Uvicorn |

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | User login with email/password |
| POST | `/auth/register` | User registration |
| POST | `/auth/google` | Google OAuth login |
| POST | `/otp/send` | Send OTP to phone |
| POST | `/otp/verify` | Verify OTP |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products/` | List all products (paginated) |
| GET | `/products/{id}` | Get product details |
| POST | `/products/` | Create product (admin) |
| PUT | `/products/update/{id}` | Update product (admin) |
| GET | `/products/{id}/variants` | Get product variants |

### Cart
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/cart/` | Get user's cart |
| POST | `/cart/add` | Add item to cart |
| PUT | `/cart/update/{id}` | Update cart item |
| DELETE | `/cart/remove/{id}` | Remove item from cart |

### Wishlist
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/wishlist/` | Get user's wishlist |
| POST | `/wishlist/add` | Add to wishlist |
| DELETE | `/wishlist/remove/{id}` | Remove from wishlist |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders/` | Get user's orders |
| POST | `/orders/create` | Create new order |
| GET | `/orders/{id}` | Get order details |

### Chatbot
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chatbot/chat` | Chat with AI assistant |
| POST | `/api/chatbot/sync-products` | Sync products to vector DB |
| GET | `/api/chatbot/status` | Chatbot status |

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest test/test_auth.py

# Run with coverage
pytest --cov=app
```

---

## 🚦 Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL
- Node.js (for Google OAuth)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/phone-shop.git
cd phone-shop
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run database migrations**
```bash
alembic upgrade head
```

6. **Start the server**
```bash
uvicorn main:app --reload
```

7. **Access API documentation**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🔧 Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT secret key |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `COHERE_API_KEY` | Cohere API key for embeddings |
| `GROQ_API_KEY` | Groq API key for LLM |
| `JWT_SECRET` | JWT authentication secret |

---

## 🤖 AI Chatbot

The project includes an AI-powered chatbot that uses:
- **Cohere Embeddings** - For vectorizing product data
- **Groq LLM (Llama 3.3)** - For natural language responses
- **PostgreSQL pgvector** - For semantic search

### How it works:
1. Products are synced to a vector database
2. User queries are embedded using Cohere
3. Similar products are retrieved using vector similarity
4. Groq LLM generates human-readable recommendations
5. Supports budget filtering, brand preferences, and more

---

## 📊 Database Schema

### Products Table
- `product_id` (PK)
- `brand`
- `model_name`
- `description`
- `base_price`
- `image_url`
- `is_active`

### Product Variants Table
- `variant_id` (PK)
- `product_id` (FK)
- `color`
- `ram`
- `storage`
- `price`
- `stock_qty`
- `sku_code`

### Users Table
- `user_id` (PK)
- `email` (unique)
- `username`
- `hashed_password`
- `phone`
- `is_verified`

### Orders Table
- `order_id` (PK)
- `user_id` (FK)
- `total_amount`
- `status`
- `created_at`

---

## 📝 API Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "detail": "Error message"
}
```

---

## 🔐 Security Features

- JWT token-based authentication
- Password hashing with bcrypt
- Google OAuth 2.0 integration
- OTP verification for phone
- CORS protection
- SQL injection prevention (via SQLAlchemy)
- Input validation with Pydantic

---

## 🚀 Deployment

### Render
The project is configured for deployment on [Render](https://render.com/).

```yaml
# render.yaml
services:
  - type: web
    name: phone-shop-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

---

## ⭐ Show Your Support

If you found this project helpful, please give it a ⭐️!

---

<div align="center">

Made with ❤️ using FastAPI

</div>
