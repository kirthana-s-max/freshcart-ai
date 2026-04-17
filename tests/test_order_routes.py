"""
Order Routes Tests
==================
Tests for order endpoints: /api/orders/*
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, orders


class TestPlaceOrder:
    """Tests for POST /api/orders endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
        self.order_items = [
            {"product_id": 1, "name": "Organic Tomatoes", "price": 3.99, "quantity": 2, "subtotal": 7.98},
            {"product_id": 7, "name": "Red Apples", "price": 4.99, "quantity": 1, "subtotal": 4.99}
        ]
        self.address = "123 Test Street, Mumbai, India"
    
    def test_place_order_success(self):
        """Test successful order placement"""
        response = self.client.post(
            "/api/orders",
            json={
                "items": self.order_items,
                "address": self.address
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"
        assert len(data["items"]) == 2
        assert "id" in data
        assert "total" in data
    
    def test_place_order_calculates_total(self):
        """Test order calculates total correctly"""
        response = self.client.post(
            "/api/orders",
            json={
                "items": self.order_items,
                "address": self.address
            }
        )
        data = response.json()
        # Total = subtotal + delivery_fee (2.99)
        expected_subtotal = 7.98 + 4.99  # 12.97
        assert data["subtotal"] == expected_subtotal
        assert data["delivery_fee"] == 2.99
        assert data["total"] == expected_subtotal + 2.99
    
    def test_place_order_empty_cart(self):
        """Test order with empty cart fails"""
        response = self.client.post(
            "/api/orders",
            json={
                "items": [],
                "address": self.address
            }
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
    
    def test_place_order_missing_items(self):
        """Test order without items fails"""
        response = self.client.post(
            "/api/orders",
            json={
                "address": self.address
            }
        )
        assert response.status_code == 422
    
    def test_place_order_missing_address(self):
        """Test order without address fails"""
        response = self.client.post(
            "/api/orders",
            json={
                "items": self.order_items
            }
        )
        assert response.status_code == 422
    
    def test_place_order_single_item(self):
        """Test order with single item"""
        response = self.client.post(
            "/api/orders",
            json={
                "items": [self.order_items[0]],
                "address": self.address
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
    
    def test_place_order_with_payment_method(self):
        """Test order with custom payment method"""
        response = self.client.post(
            "/api/orders",
            json={
                "items": self.order_items,
                "address": self.address,
                "payment_method": "card"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["payment_method"] == "card"
    
    def test_place_order_default_payment_method(self):
        """Test order with default payment method (COD)"""
        response = self.client.post(
            "/api/orders",
            json={
                "items": self.order_items,
                "address": self.address
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["payment_method"] == "cod"
    
    def test_place_order_with_auth(self):
        """Test placing order with authentication"""
        # Login first
        login_response = self.client.post(
            "/api/auth/login",
            json={
                "email": "demo@freshcart.ai",
                "password": "demo123"
            }
        )
        token = login_response.json()["token"]
        
        # Place order with auth
        response = self.client.post(
            "/api/orders",
            json={
                "items": self.order_items,
                "address": self.address
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        # User ID should be set when authenticated
        assert data.get("user_id") is not None


class TestGetOrders:
    """Tests for GET /api/orders endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_orders(self):
        """Test getting orders list"""
        response = self.client.get("/api/orders")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_orders_returns_list(self):
        """Test that orders endpoint returns a list"""
        response = self.client.get("/api/orders")
        assert isinstance(response.json(), list)


class TestGetOrderById:
    """Tests for GET /api/orders/{order_id} endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
        # Create an order first
        response = self.client.post(
            "/api/orders",
            json={
                "items": [
                    {"product_id": 1, "name": "Tomato", "price": 3.99, "quantity": 1, "subtotal": 3.99}
                ],
                "address": "123 Test St"
            }
        )
        self.order_id = response.json()["id"]
    
    def test_get_order_valid_id(self):
        """Test getting order with valid ID"""
        response = self.client.get(f"/api/orders/{self.order_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.order_id
    
    def test_get_order_invalid_id(self):
        """Test getting order with non-existent ID"""
        response = self.client.get("/api/orders/9999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_order_structure(self):
        """Test order has required fields"""
        response = self.client.get(f"/api/orders/{self.order_id}")
        data = response.json()
        required_fields = ["id", "items", "subtotal", "delivery_fee", "total", "status", "address"]
        for field in required_fields:
            assert field in data


class TestTrackOrder:
    """Tests for GET /api/orders/track/{order_id} endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
        # Create an order first
        response = self.client.post(
            "/api/orders",
            json={
                "items": [
                    {"product_id": 1, "name": "Tomato", "price": 3.99, "quantity": 1, "subtotal": 3.99}
                ],
                "address": "123 Test St"
            }
        )
        self.order_id = response.json()["id"]
    
    def test_track_order_valid_id(self):
        """Test tracking order with valid ID"""
        response = self.client.get(f"/api/orders/track/{self.order_id}")
        assert response.status_code == 200
        data = response.json()
        assert "order_id" in data
        assert "status" in data
        assert "timeline" in data
    
    def test_track_order_invalid_id(self):
        """Test tracking non-existent order"""
        response = self.client.get("/api/orders/track/9999")
        assert response.status_code == 404
    
    def test_track_order_timeline_structure(self):
        """Test order timeline has correct structure"""
        response = self.client.get(f"/api/orders/track/{self.order_id}")
        data = response.json()
        timeline = data["timeline"]
        assert isinstance(timeline, list)
        assert len(timeline) == 4  # confirmed, preparing, out_for_delivery, delivered
        
        for step in timeline:
            assert "status" in step
            assert "completed" in step
    
    def test_track_order_initial_status(self):
        """Test new order has 'confirmed' status"""
        response = self.client.get(f"/api/orders/track/{self.order_id}")
        data = response.json()
        assert data["status"] == "confirmed"
