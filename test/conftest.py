import pytest
from test.config import *
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_db, Base
from main import app
from app.models import User, Product, ProductVariant
from app.utils import hash_password
from app.oauth2 import create_access_token

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        phone_number="1234567890",
        hashed_password=hash_password("testpass123"),
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_user2(db_session):
    user = User(
        username="testuser2",
        email="test2@example.com",
        phone_number="0987654321",
        hashed_password=hash_password("testpass456"),
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_token(test_user):
    token = create_access_token(data={"user_id": test_user.user_id})
    return token

@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def test_product(db_session):
    product = Product(
        brand="Apple",
        model_name="iPhone 15 Pro",
        description="Latest iPhone model",
        base_price=999.99,
        image_url="http://example.com/iphone.jpg",
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product

@pytest.fixture
def test_variant(db_session, test_product):
    variant = ProductVariant(
        product_id=test_product.product_id,
        color="Space Black",
        ram="8GB",
        storage="256GB",
        price=1099.99,
        stock_qty=50,
        sku_code="IPHONE15-BLK-256",
        image_url="http://example.com/iphone-black.jpg"
    )
    db_session.add(variant)
    db_session.commit()
    db_session.refresh(variant)
    return variant

@pytest.fixture
def test_variant2(db_session, test_product):
    variant = ProductVariant(
        product_id=test_product.product_id,
        color="Natural Titanium",
        ram="8GB",
        storage="512GB",
        price=1299.99,
        stock_qty=30,
        sku_code="IPHONE15-TIT-512",
        image_url="http://example.com/iphone-titanium.jpg"
    )
    db_session.add(variant)
    db_session.commit()
    db_session.refresh(variant)
    return variant
