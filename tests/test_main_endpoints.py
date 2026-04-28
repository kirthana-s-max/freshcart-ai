"""
Main Endpoints Tests
====================
Tests for root and health check endpoints
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint returns welcome message"""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    def test_root_has_docs_link(self):
        """Test root endpoint includes docs link"""
        response = self.client.get("/")
        data = response.json()
        assert "docs" in data


class TestHealthEndpoint:
    """Tests for GET /api/health endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_health_includes_stats(self):
        """Test health check includes system stats"""
        response = self.client.get("/api/health")
        data = response.json()
        assert "products" in data
        assert "orders" in data
        assert "subscriptions" in data
    
    def test_health_products_count(self):
        """Test health check returns valid products count"""
        response = self.client.get("/api/health")
        data = response.json()
        assert isinstance(data["products"], int)
        assert data["products"] > 0


class TestCartAdd:
    """Tests for POST /api/cart/add endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_add_to_cart_valid_product(self):
        """Test adding valid product to cart"""
        response = self.client.post(
            "/api/cart/add",
            params={"product_id": 1, "quantity": 2}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Added to cart"
        assert "product" in data
        assert data["quantity"] == 2
    
    def test_add_to_cart_invalid_product(self):
        """Test adding invalid product to cart"""
        response = self.client.post(
            "/api/cart/add",
            params={"product_id": 9999, "quantity": 1}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_add_to_cart_default_quantity(self):
        """Test adding to cart with default quantity"""
        response = self.client.post(
            "/api/cart/add",
            params={"product_id": 1}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 1
    
    def test_add_to_cart_zero_quantity(self):
        """Test adding zero quantity to cart"""
        response = self.client.post(
            "/api/cart/add",
            params={"product_id": 1, "quantity": 0}
        )
        # Should accept or reject depending on implementation
        assert response.status_code in [200, 422]
    
    def test_add_to_cart_negative_quantity(self):
        """Test adding negative quantity to cart"""
        response = self.client.post(
            "/api/cart/add",
            params={"product_id": 1, "quantity": -1}
        )
        assert response.status_code == 422 
