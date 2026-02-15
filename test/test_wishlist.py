import pytest
from fastapi import status

def test_add_to_wishlist_success(client, test_product, auth_headers):
    wishlist_data = {
        "product_id": test_product.product_id
    }
    response = client.post("/wishlist/add", json=wishlist_data, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "wishlist_id" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["product"]["product_id"] == test_product.product_id

def test_add_to_wishlist_unauthorized(client, test_product):
    wishlist_data = {
        "product_id": test_product.product_id
    }
    response = client.post("/wishlist/add", json=wishlist_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_add_to_wishlist_product_not_found(client, auth_headers):
    wishlist_data = {
        "product_id": 9999
    }
    response = client.post("/wishlist/add", json=wishlist_data, headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Product not found"

def test_add_to_wishlist_duplicate_product(client, test_product, auth_headers):
    wishlist_data = {
        "product_id": test_product.product_id
    }
    response1 = client.post("/wishlist/add", json=wishlist_data, headers=auth_headers)
    assert response1.status_code == status.HTTP_200_OK
    
    response2 = client.post("/wishlist/add", json=wishlist_data, headers=auth_headers)
    assert response2.status_code == status.HTTP_200_OK
    data = response2.json()
    assert len(data["items"]) == 1

def test_view_wishlist_empty(client, auth_headers):
    response = client.get("/wishlist/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "wishlist_id" in data
    assert data["items"] == []

def test_view_wishlist_unauthorized(client):
    response = client.get("/wishlist/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_view_wishlist_with_items(client, test_product, auth_headers):
    wishlist_data = {
        "product_id": test_product.product_id
    }
    client.post("/wishlist/add", json=wishlist_data, headers=auth_headers)
    
    response = client.get("/wishlist/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["product"]["product_id"] == test_product.product_id
    assert data["items"][0]["product"]["brand"] == test_product.brand

def test_remove_from_wishlist_success(client, test_product, auth_headers):
    wishlist_data = {
        "product_id": test_product.product_id
    }
    add_response = client.post("/wishlist/add", json=wishlist_data, headers=auth_headers)
    wishlist_item_id = add_response.json()["items"][0]["wishlist_item_id"]
    
    response = client.delete(f"/wishlist/remove/{wishlist_item_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    wishlist_response = client.get("/wishlist/", headers=auth_headers)
    assert len(wishlist_response.json()["items"]) == 0

def test_remove_from_wishlist_unauthorized(client):
    response = client.delete("/wishlist/remove/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_remove_from_wishlist_item_not_found(client, auth_headers):
    response = client.delete("/wishlist/remove/9999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Item not found"
