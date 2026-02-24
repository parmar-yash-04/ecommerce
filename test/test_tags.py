import pytest
from fastapi import status

def test_list_tags_empty(client):
    response = client.get("/tags/tags")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == []

def test_create_tag_success(client, auth_headers):
    tag_data = {"name": "Smartphone"}
    response = client.post("/tags/tags", json=tag_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Smartphone"
    assert "tag_id" in data

def test_create_tag_duplicate(client, auth_headers):
    tag_data = {"name": "5G"}
    client.post("/tags/tags", json=tag_data, headers=auth_headers)
    
    response = client.post("/tags/tags", json=tag_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_list_tags_with_data(client, auth_headers):
    client.post("/tags/tags", json={"name": "5G"}, headers=auth_headers)
    client.post("/tags/tags", json={"name": "RAM"}, headers=auth_headers)
    
    response = client.get("/tags/tags")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2
    tag_names = [tag["name"] for tag in data]
    assert "5G" in tag_names
    assert "RAM" in tag_names

def test_get_products_by_tag_empty(client, auth_headers):
    # Create a tag
    tag_response = client.post("/tags/tags", json={"name": "Smartphone"}, headers=auth_headers)
    tag_id = tag_response.json()["tag_id"]
    
    response = client.get(f"/tags/tags/{tag_id}/products")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == []

def test_get_products_by_tag_with_products(client, auth_headers, test_product):
    # Create a tag
    tag_response = client.post("/tags/tags", json={"name": "Smartphone"}, headers=auth_headers)
    tag_id = tag_response.json()["tag_id"]
    
    # Add tag to product (using product creation with tag_ids)
    product_data = {
        "brand": "Samsung",
        "model_name": "Galaxy S24",
        "description": "Test product",
        "base_price": 899.99,
        "image_url": "http://example.com/galaxy.jpg",
        "is_active": True,
        "tag_ids": [tag_id]
    }
    client.post("/products/", json=product_data, headers=auth_headers)
    
    # Get products by tag
    response = client.get(f"/tags/tags/{tag_id}/products")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert data[0]["brand"] == "Samsung"
    assert data[0]["model_name"] == "Galaxy S24"

def test_get_products_by_tag_not_found(client):
    response = client.get("/tags/tags/99999/products")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == []

def test_create_tag_no_auth_required(client):
    """Test creating tag without authentication (endpoint is intentionally open)"""
    tag_data = {"name": "TestTag"}
    response = client.post("/tags/tags", json=tag_data)
    assert response.status_code in [200, 201]