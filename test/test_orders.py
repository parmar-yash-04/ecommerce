import pytest
from fastapi import status
from app.models import OTPVerification

def get_otp_from_db(db_session, email):
    otp_record = db_session.query(OTPVerification).filter(
        OTPVerification.email == email
    ).order_by(OTPVerification.created_at.desc()).first()
    return otp_record.otp_code if otp_record else None

def test_get_my_orders_empty(client, auth_headers):
    response = client.get("/orders/my", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_get_my_orders_unauthorized(client):
    response = client.get("/orders/my")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_my_orders_with_single_order(client, test_variant, auth_headers, db_session):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 3
    }
    client.post("/cart/add", json=cart_data, headers=auth_headers)
    
    client.post("/otp/send", json={"email": "test@example.com"})
    otp_code = get_otp_from_db(db_session, "test@example.com")
    
    client.post("/otp/verify", json={"email": "test@example.com", "otp": otp_code})
    
    checkout_data = {
        "email": "test@example.com",
        "otp": otp_code,
        "shipping_address": "123 Main St, City, State 12345"
    }
    order_response = client.post("/checkout/place-order", json=checkout_data, headers=auth_headers)
    order_id = order_response.json()["order"]["order_id"]
    
    response = client.get("/orders/my", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["order_id"] == order_id
    assert data[0]["order_status"] == "placed"

def test_get_my_orders_with_multiple_orders(client, test_variant, test_variant2, auth_headers, db_session):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 1
    }
    client.post("/cart/add", json=cart_data, headers=auth_headers)
    
    client.post("/otp/send", json={"email": "test@example.com"})
    otp_code1 = get_otp_from_db(db_session, "test@example.com")
    
    client.post("/otp/verify", json={"email": "test@example.com", "otp": otp_code1})
    
    checkout_data1 = {
        "email": "test@example.com",
        "otp": otp_code1,
        "shipping_address": "123 Main St"
    }
    client.post("/checkout/place-order", json=checkout_data1, headers=auth_headers)
    
    cart_data2 = {
        "variant_id": test_variant2.variant_id,
        "quantity": 2
    }
    client.post("/cart/add", json=cart_data2, headers=auth_headers)
    
    client.post("/otp/send", json={"email": "test@example.com"})
    otp_code2 = get_otp_from_db(db_session, "test@example.com")
    
    client.post("/otp/verify", json={"email": "test@example.com", "otp": otp_code2})
    
    checkout_data2 = {
        "email": "test@example.com",
        "otp": otp_code2,
        "shipping_address": "456 Second Ave"
    }
    client.post("/checkout/place-order", json=checkout_data2, headers=auth_headers)
    
    response = client.get("/orders/my", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2

def test_get_order_detail_success(client, test_variant, auth_headers, db_session):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 2
    }
    client.post("/cart/add", json=cart_data, headers=auth_headers)
    
    client.post("/otp/send", json={"email": "test@example.com"})
    otp_code = get_otp_from_db(db_session, "test@example.com")
    
    client.post("/otp/verify", json={"email": "test@example.com", "otp": otp_code})
    
    checkout_data = {
        "email": "test@example.com",
        "otp": otp_code,
        "shipping_address": "123 Main St"
    }
    order_response = client.post("/checkout/place-order", json=checkout_data, headers=auth_headers)
    order_id = order_response.json()["order"]["order_id"]
    
    response = client.get(f"/orders/{order_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["order_id"] == order_id
    assert data["order_status"] == "placed"
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2

def test_get_order_detail_unauthorized(client):
    response = client.get("/orders/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_order_detail_not_found(client, auth_headers):
    response = client.get("/orders/9999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Order not found"

def test_get_order_detail_different_user(client, test_variant, auth_headers, test_user2, db_session):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 1
    }
    client.post("/cart/add", json=cart_data, headers=auth_headers)
    
    client.post("/otp/send", json={"email": "test@example.com"})
    otp_code = get_otp_from_db(db_session, "test@example.com")
    
    client.post("/otp/verify", json={"email": "test@example.com", "otp": otp_code})
    
    checkout_data = {
        "email": "test@example.com",
        "otp": otp_code,
        "shipping_address": "123 Main St"
    }
    order_response = client.post("/checkout/place-order", json=checkout_data, headers=auth_headers)
    order_id = order_response.json()["order"]["order_id"]
    
    from app.oauth2 import create_access_token
    token2 = create_access_token(data={"user_id": test_user2.user_id})
    auth_headers2 = {"Authorization": f"Bearer {token2}"}
    
    response = client.get(f"/orders/{order_id}", headers=auth_headers2)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Order not found"

def test_order_contains_correct_items(client, test_variant, test_variant2, auth_headers, db_session):
    cart_data1 = {
        "variant_id": test_variant.variant_id,
        "quantity": 2
    }
    client.post("/cart/add", json=cart_data1, headers=auth_headers)
    
    cart_data2 = {
        "variant_id": test_variant2.variant_id,
        "quantity": 3
    }
    client.post("/cart/add", json=cart_data2, headers=auth_headers)
    
    client.post("/otp/send", json={"email": "test@example.com"})
    otp_code = get_otp_from_db(db_session, "test@example.com")
    
    client.post("/otp/verify", json={"email": "test@example.com", "otp": otp_code})
    
    checkout_data = {
        "email": "test@example.com",
        "otp": otp_code,
        "shipping_address": "123 Main St"
    }
    order_response = client.post("/checkout/place-order", json=checkout_data, headers=auth_headers)
    order_id = order_response.json()["order"]["order_id"]
    
    response = client.get(f"/orders/{order_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 2
    
    variant_ids = [item["variant_id"] for item in data["items"]]
    assert test_variant.variant_id in variant_ids
    assert test_variant2.variant_id in variant_ids
