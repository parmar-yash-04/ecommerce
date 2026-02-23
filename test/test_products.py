import pytest
from fastapi import status

def test_create_product_success(client, auth_headers):
    product_data = {
        "brand": "Samsung",
        "model_name": "Galaxy S24",
        "description": "Latest Samsung flagship",
        "base_price": 899.99,
        "image_url": "http://example.com/galaxy.jpg",
        "is_active": True
    }
    response = client.post("/products/", json=product_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["brand"] == product_data["brand"]
    assert data["model_name"] == product_data["model_name"]
    assert data["base_price"] == product_data["base_price"]
    assert "product_id" in data

def test_create_product_unauthorized(client):
    product_data = {
        "brand": "Samsung",
        "model_name": "Galaxy S24",
        "description": "Latest Samsung flagship",
        "base_price": 899.99
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_product_missing_fields(client, auth_headers):
    product_data = {
        "brand": "Samsung"
    }
    response = client.post("/products/", json=product_data, headers=auth_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_list_products_empty(client):
    response = client.get("/products/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["size"] == 10
    assert data["total_pages"] == 0
    assert data["data"] == []

def test_list_products(client, test_product):
    response = client.get("/products/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["product_id"] == test_product.product_id
    assert data["data"][0]["brand"] == test_product.brand

def test_get_product_success(client, test_product):
    response = client.get(f"/products/{test_product.product_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["product_id"] == test_product.product_id
    assert data["brand"] == test_product.brand

def test_get_product_not_found(client):
    response = client.get("/products/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Product not found"

def test_create_variant_success(client, test_product, auth_headers):
    variant_data = {
        "product_id": test_product.product_id,
        "color": "Blue",
        "ram": "12GB",
        "storage": "512GB",
        "price": 1199.99,
        "stock_qty": 25,
        "sku_code": "IPHONE15-BLUE-512",
        "image_url": "http://example.com/blue.jpg"
    }
    response = client.post("/products/variants", json=variant_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["product_id"] == test_product.product_id
    assert data["color"] == variant_data["color"]
    assert data["sku_code"] == variant_data["sku_code"]
    assert "variant_id" in data

def test_create_variant_unauthorized(client, test_product):
    variant_data = {
        "product_id": test_product.product_id,
        "color": "Blue",
        "ram": "12GB",
        "storage": "512GB",
        "price": 1199.99,
        "stock_qty": 25,
        "sku_code": "IPHONE15-BLUE-512"
    }
    response = client.post("/products/variants", json=variant_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_variant_product_not_found(client, auth_headers):
    variant_data = {
        "product_id": 9999,
        "color": "Blue",
        "ram": "12GB",
        "storage": "512GB",
        "price": 1199.99,
        "stock_qty": 25,
        "sku_code": "NOTFOUND-BLUE-512"
    }
    response = client.post("/products/variants", json=variant_data, headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Product not found"

def test_create_variant_duplicate_sku(client, test_product, test_variant, auth_headers):
    variant_data = {
        "product_id": test_product.product_id,
        "color": "Red",
        "ram": "8GB",
        "storage": "128GB",
        "price": 999.99,
        "stock_qty": 10,
        "sku_code": test_variant.sku_code
    }
    response = client.post("/products/variants", json=variant_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "sku_code already exists"

def test_get_product_with_variants_success(client, test_product, test_variant, test_variant2):
    response = client.get(f"/products/{test_product.product_id}/variants")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["model_name"] == test_product.model_name
    assert len(data["variants"]) == 2
    assert data["variants"][0]["variant_id"] == test_variant.variant_id
    assert data["variants"][1]["variant_id"] == test_variant2.variant_id

def test_get_product_with_variants_no_variants(client, test_product):
    response = client.get(f"/products/{test_product.product_id}/variants")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["model_name"] == test_product.model_name
    assert data["variants"] == []

def test_get_product_with_variants_not_found(client):
    response = client.get("/products/9999/variants")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Product not found"
