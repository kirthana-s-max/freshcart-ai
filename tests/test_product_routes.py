"""
Product Routes Tests
====================
Tests for product endpoints: /api/products/*, /api/search, /api/categories
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app


class TestGetProducts:
    """Tests for GET /api/products endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_all_products(self):
        """Test getting all products"""
        response = self.client.get("/api/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Verify product structure
        if data:
            assert "id" in data[0]
            assert "name" in data[0]
            assert "price" in data[0]
            assert "category" in data[0]
    
    def test_get_products_returns_vegetables(self):
        """Test that products include vegetables"""
        response = self.client.get("/api/products")
        data = response.json()
        categories = [p["category"] for p in data]
        assert "vegetables" in categories
    
    def test_get_products_returns_fruits(self):
        """Test that products include fruits"""
        response = self.client.get("/api/products")
        data = response.json()
        categories = [p["category"] for p in data]
        assert "fruits" in categories
    
    def test_get_products_returns_nuts(self):
        """Test that products include nuts"""
        response = self.client.get("/api/products")
        data = response.json()
        categories = [p["category"] for p in data]
        assert "nuts" in categories
    
    def test_get_products_contains_required_fields(self):
        """Test that products have all required fields"""
        response = self.client.get("/api/products")
        data = response.json()
        for product in data:
            assert "id" in product
            assert "name" in product
            assert "category" in product
            assert "price" in product
            assert "unit" in product
            assert "stock" in product
            assert "description" in product


class TestGetProductById:
    """Tests for GET /api/products/{product_id} endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_product_valid_id(self):
        """Test getting product with valid ID"""
        response = self.client.get("/api/products/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Organic Tomatoes"
    
    def test_get_product_invalid_id(self):
        """Test getting product with non-existent ID"""
        response = self.client.get("/api/products/9999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_product_zero_id(self):
        """Test getting product with ID 0"""
        response = self.client.get("/api/products/0")
        assert response.status_code == 404
    
    def test_get_product_negative_id(self):
        """Test getting product with negative ID"""
        response = self.client.get("/api/products/-1")
        assert response.status_code == 404
    
    def test_get_product_string_id(self):
        """Test getting product with string ID (type error)"""
        response = self.client.get("/api/products/abc")
        assert response.status_code == 422  # Validation error


class TestGetProductsByCategory:
    """Tests for GET /api/products/category/{category} endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_vegetables(self):
        """Test getting vegetables category"""
        response = self.client.get("/api/products/category/vegetables")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for product in data:
            assert product["category"].lower() == "vegetables"
    
    def test_get_fruits(self):
        """Test getting fruits category"""
        response = self.client.get("/api/products/category/fruits")
        assert response.status_code == 200
        data = response.json()
        for product in data:
            assert product["category"].lower() == "fruits"
    
    def test_get_nuts(self):
        """Test getting nuts category"""
        response = self.client.get("/api/products/category/nuts")
        assert response.status_code == 200
        data = response.json()
        for product in data:
            assert product["category"].lower() == "nuts"
    
    def test_category_case_insensitive(self):
        """Test category search is case insensitive"""
        response = self.client.get("/api/products/category/VEGETABLES")
        assert response.status_code == 200
        data = response.json()
        for product in data:
            assert product["category"].lower() == "vegetables"
    
    def test_category_mixed_case(self):
        """Test category search with mixed case"""
        response = self.client.get("/api/products/category/FrUiTs")
        assert response.status_code == 200
        data = response.json()
        for product in data:
            assert product["category"].lower() == "fruits"
    
    def test_invalid_category(self):
        """Test getting non-existent category"""
        response = self.client.get("/api/products/category/nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_empty_category_name(self):
        """Test getting empty category name"""
        response = self.client.get("/api/products/category/")
        # Should return all products or 404
        assert response.status_code in [200, 404]


class TestSearchProducts:
    """Tests for GET /api/search endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_search_by_name(self):
        """Test searching by product name"""
        response = self.client.get("/api/search?q=tomato")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Results should contain "tomato" in name
        for product in data:
            assert "tomato" in product["name"].lower()
    
    def test_search_by_category(self):
        """Test searching by category"""
        response = self.client.get("/api/search?q=vegetables")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for product in data:
            assert "vegetables" in [product["category"].lower(), product["name"].lower(), product["description"].lower()]
    
    def test_search_no_results(self):
        """Test search with no matching results"""
        response = self.client.get("/api/search?q=nonexistentproductxyz")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_search_case_insensitive(self):
        """Test search is case insensitive"""
        response1 = self.client.get("/api/search?q=TOMATO")
        response2 = self.client.get("/api/search?q=tomato")
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(response1.json()) == len(response2.json())
    
    def test_search_partial_match(self):
        """Test partial word match"""
        response = self.client.get("/api/search?q=app")
        assert response.status_code == 200
        data = response.json()
        # Should match "Apple" products
        assert any("apple" in p["name"].lower() for p in data)
    
    def test_search_special_characters(self):
        """Test search with special characters"""
        response = self.client.get("/api/search?q=@#$%")
        assert response.status_code == 200
        # Should return empty or handle gracefully
    
    def test_search_empty_query(self):
        """Test search with empty query"""
        response = self.client.get("/api/search?q=")
        assert response.status_code == 200


class TestGetCategories:
    """Tests for GET /api/categories endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_categories(self):
        """Test getting all categories"""
        response = self.client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # At least vegetables, fruits, nuts
    
    def test_categories_include_expected(self):
        """Test that expected categories are present"""
        response = self.client.get("/api/categories")
        data = response.json()
        categories = [c.lower() for c in data]
        assert "vegetables" in categories
        assert "fruits" in categories
        assert "nuts" in categories
    
    def test_categories_no_duplicates(self):
        """Test that categories list has no duplicates"""
        response = self.client.get("/api/categories")
        data = response.json()
        assert len(data) == len(set(data))
