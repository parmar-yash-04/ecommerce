import pytest
from fastapi import status
from app.models import Cart, CartItem

def test_place_order_success(client, test_variant, auth_headers, db_session):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 2
    }
    client.post("/cart/add", json=cart_data, headers=auth_headers)
    
    otp_response = client.post("/otp/send", json={"email": "test@example.com"})
    otp_code = otp_response.json()["otp"]
    
    checkout_data = {
        "email": "test@example.com",
        "otp": otp_code,
        "shipping_address": "123 Main St, City, State 12345"
    }
    
    initial_stock = test_variant.stock_qty
    
    response = client.post("/checkout/place-order", json=checkout_data, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "order_id" in data
    assert "order_number" in data
    assert data["order_status"] == "placed"
    assert data["total_amount"] == test_variant.price * 2
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2
    
    db_session.refresh(test_variant)
    assert test_variant.stock_qty == initial_stock - 2
    
    cart_response = client.get("/cart/", headers=auth_headers)
    assert len(cart_response.json()["items"]) == 0

def test_place_order_unauthorized(client):
    checkout_data = {
        "email": "test@example.com",
        "otp": "123456",
        "shipping_address": "123 Main St"
    }
    response = client.post("/checkout/place-order", json=checkout_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_place_order_invalid_otp(client, test_variant, auth_headers):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 1
    }
    client.post("/cart/add", json=cart_data, headers=auth_headers)
    
    checkout_data = {
        "email": "test@example.com",
        "otp": "000000",
        "shipping_address": "123 Main St"
    }
    response = client.post("/checkout/place-order", json=checkout_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "OTP invalid or expired"

def test_place_order_empty_cart(client, auth_headers):
    otp_response = client.post("/otp/send", json={"email": "test@example.com"})
    otp_code = otp_response.json()["otp"]
    
    checkout_data = {
        "email": "test@example.com",
        "otp": otp_code,
        "shipping_address": "123 Main St"
    }
    response = client.post("/checkout/place-order", json=checkout_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Cart is empty"

def test_place_order_insufficient_stock(client, test_variant, auth_headers, db_session):
    test_variant.stock_qty = 1
    db_session.commit()
    
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 1
    }
    client.post("/cart/add", json=cart_data, headers=auth_headers)
    
    db_session.refresh(test_variant)
    test_variant.stock_qty = 0
    db_session.commit()
    
    otp_response = client.post("/otp/send", json={"email": "test@example.com"})
    otp_code = otp_response.json()["otp"]
    
    checkout_data = {
        "email": "test@example.com",
        "otp": otp_code,
        "shipping_address": "123 Main St"
    }
    response = client.post("/checkout/place-order", json=checkout_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Not enough stock" in response.json()["detail"]

def test_place_order_multiple_items(client, test_variant, test_variant2, auth_headers, db_session):
    cart_data1 = {
        "variant_id": test_variant.variant_id,
        "quantity": 2
    }
    client.post("/cart/add", json=cart_data1, headers=auth_headers)
    
    cart_data2 = {
        "variant_id": test_variant2.variant_id,
        "quantity": 1
    }
    client.post("/cart/add", json=cart_data2, headers=auth_headers)
    
    otp_response = client.post("/otp/send", json={"email": "test@example.com"})
    otp_code = otp_response.json()["otp"]
    
    checkout_data = {
        "email": "test@example.com",
        "otp": otp_code,
        "shipping_address": "123 Main St"
    }
    response = client.post("/checkout/place-order", json=checkout_data, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 2
    expected_total = (test_variant.price * 2) + (test_variant2.price * 1)
    assert data["total_amount"] == expected_total

def test_place_order_missing_shipping_address(client, test_variant, auth_headers):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 1
    }
    client.post("/cart/add", json=cart_data, headers=auth_headers)
    
    otp_response = client.post("/otp/send", json={"email": "test@example.com"})
    otp_code = otp_response.json()["otp"]
    
    checkout_data = {
        "email": "test@example.com",
        "otp": otp_code
    }
    response = client.post("/checkout/place-order", json=checkout_data, headers=auth_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_my_orders_empty(client, auth_headers):
    response = client.get("/checkout/my-orders", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_my_orders_unauthorized(client):
    response = client.get("/checkout/my-orders")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_my_orders_with_order(client, test_variant, auth_headers):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 1
    }
    client.post("/cart/add", json=cart_data, headers=auth_headers)
    
    otp_response = client.post("/otp/send", json={"email": "test@example.com"})
    otp_code = otp_response.json()["otp"]
    
    checkout_data = {
        "email": "test@example.com",
        "otp": otp_code,
        "shipping_address": "123 Main St"
    }
    order_response = client.post("/checkout/place-order", json=checkout_data, headers=auth_headers)
    order_id = order_response.json()["order_id"]
    
    response = client.get("/checkout/my-orders", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["order_id"] == order_id
