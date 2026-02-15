import pytest
from fastapi import status

def test_add_to_cart_success(client, test_variant, auth_headers):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 2
    }
    response = client.post("/cart/add", json=cart_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "cart_id" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["variant_id"] == test_variant.variant_id
    assert data["items"][0]["quantity"] == 2

def test_add_to_cart_unauthorized(client, test_variant):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 2
    }
    response = client.post("/cart/add", json=cart_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_add_to_cart_variant_not_found(client, auth_headers):
    cart_data = {
        "variant_id": 9999,
        "quantity": 2
    }
    response = client.post("/cart/add", json=cart_data, headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Variant not found"

def test_add_to_cart_invalid_quantity(client, test_variant, auth_headers):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 0
    }
    response = client.post("/cart/add", json=cart_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Quantity must be greater than 0"

def test_add_to_cart_negative_quantity(client, test_variant, auth_headers):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": -1
    }
    response = client.post("/cart/add", json=cart_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Quantity must be greater than 0"

def test_add_to_cart_exceeds_stock(client, test_variant, auth_headers):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 100
    }
    response = client.post("/cart/add", json=cart_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Not enough stock available"

def test_add_to_cart_existing_item(client, test_variant, auth_headers):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 2
    }
    response1 = client.post("/cart/add", json=cart_data, headers=auth_headers)
    assert response1.status_code == status.HTTP_201_CREATED
    
    response2 = client.post("/cart/add", json=cart_data, headers=auth_headers)
    assert response2.status_code == status.HTTP_201_CREATED
    data = response2.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 4

def test_view_cart_empty(client, auth_headers):
    response = client.get("/cart/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "cart_id" in data
    assert data["items"] == []

def test_view_cart_unauthorized(client):
    response = client.get("/cart/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_view_cart_with_items(client, test_variant, auth_headers):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 3
    }
    client.post("/cart/add", json=cart_data, headers=auth_headers)
    
    response = client.get("/cart/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 3

def test_update_cart_quantity(client, test_variant, auth_headers):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 2
    }
    add_response = client.post("/cart/add", json=cart_data, headers=auth_headers)
    cart_item_id = add_response.json()["items"][0]["cart_item_id"]
    
    update_data = {
        "cart_item_id": cart_item_id,
        "quantity": 5
    }
    response = client.put("/cart/update", json=update_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["items"][0]["quantity"] == 5

def test_update_cart_quantity_to_zero_removes_item(client, test_variant, auth_headers):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 2
    }
    add_response = client.post("/cart/add", json=cart_data, headers=auth_headers)
    cart_item_id = add_response.json()["items"][0]["cart_item_id"]
    
    update_data = {
        "cart_item_id": cart_item_id,
        "quantity": 0
    }
    response = client.put("/cart/update", json=update_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert len(data["items"]) == 0

def test_update_cart_unauthorized(client):
    update_data = {
        "cart_item_id": 1,
        "quantity": 5
    }
    response = client.put("/cart/update", json=update_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_cart_item_not_found(client, auth_headers):
    update_data = {
        "cart_item_id": 9999,
        "quantity": 5
    }
    response = client.put("/cart/update", json=update_data, headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Cart item not found"

def test_remove_item_success(client, test_variant, auth_headers):
    cart_data = {
        "variant_id": test_variant.variant_id,
        "quantity": 2
    }
    add_response = client.post("/cart/add", json=cart_data, headers=auth_headers)
    cart_item_id = add_response.json()["items"][0]["cart_item_id"]
    
    response = client.delete(f"/cart/remove/{cart_item_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    cart_response = client.get("/cart/", headers=auth_headers)
    assert len(cart_response.json()["items"]) == 0

def test_remove_item_unauthorized(client):
    response = client.delete("/cart/remove/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_remove_item_not_found(client, auth_headers):
    response = client.delete("/cart/remove/9999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Item not found"
