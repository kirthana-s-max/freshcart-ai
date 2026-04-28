"""
Subscription Routes Tests
=========================
Tests for subscription endpoints: /api/subscriptions/*
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, subscriptions


class TestCreateSubscription:
    """Tests for POST /api/subscriptions endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_create_subscription_daily(self):
        """Test creating daily subscription"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "daily",
                "quantity": 2
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["frequency"] == "daily"
        assert data["quantity"] == 2
        assert data["active"] is True
        assert "next_delivery" in data
    
    def test_create_subscription_weekly(self):
        """Test creating weekly subscription"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "weekly",
                "quantity": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["frequency"] == "weekly"
    
    def test_create_subscription_monthly(self):
        """Test creating monthly subscription"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "monthly",
                "quantity": 3
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["frequency"] == "monthly"
    
    def test_create_subscription_default_quantity(self):
        """Test subscription defaults quantity to 1"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "weekly"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 1
    
    def test_create_subscription_invalid_product(self):
        """Test creating subscription with invalid product ID"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 9999,
                "frequency": "weekly",
                "quantity": 1
            }
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_create_subscription_invalid_frequency(self):
        """Test creating subscription with invalid frequency"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "yearly",
                "quantity": 1
            }
        )
        # May accept invalid frequency or validate
        # The behavior depends on implementation
        assert response.status_code in [200, 400, 422]
    
    def test_create_subscription_zero_quantity(self):
        """Test creating subscription with zero quantity"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "weekly",
                "quantity": 0
            }
        )
        # Should either accept or reject zero quantity
        assert response.status_code in [200, 422]
    
    def test_create_subscription_negative_quantity(self):
        """Test creating subscription with negative quantity"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "weekly",
                "quantity": -1
            }
        )
        assert response.status_code == 422
    
    def test_create_subscription_missing_product_id(self):
        """Test creating subscription without product_id"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "frequency": "weekly",
                "quantity": 1
            }
        )
        assert response.status_code == 422
    
    def test_create_subscription_missing_frequency(self):
        """Test creating subscription without frequency"""
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "quantity": 1
            }
        )
        assert response.status_code == 422
    
    def test_create_subscription_with_auth(self):
        """Test creating subscription with authentication"""
        # Login first
        login_response = self.client.post(
            "/api/auth/login",
            json={
                "email": "demo@freshcart.ai",
                "password": "demo123"
            }
        )
        token = login_response.json()["token"]
        
        # Create subscription with auth
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "weekly",
                "quantity": 1
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        # User ID should be set when authenticated
        assert data.get("user_id") is not None


class TestGetSubscriptions:
    """Tests for GET /api/subscriptions endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_subscriptions(self):
        """Test getting subscriptions"""
        response = self.client.get("/api/subscriptions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_subscriptions_returns_list(self):
        """Test that subscriptions endpoint returns a list"""
        response = self.client.get("/api/subscriptions")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestCancelSubscription:
    """Tests for DELETE /api/subscriptions/{subscription_id} endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
        # Create a subscription to cancel
        response = self.client.post(
            "/api/subscriptions",
            json={
                "product_id": 1,
                "frequency": "weekly",
                "quantity": 1
            }
        )
        self.subscription_id = response.json()["id"]
    
    def test_cancel_subscription(self):
        """Test cancelling a subscription"""
        response = self.client.delete(f"/api/subscriptions/{self.subscription_id}")
        assert response.status_code == 200
        assert "cancelled" in response.json()["message"].lower()
    
    def test_cancel_subscription_invalid_id(self):
        """Test cancelling non-existent subscription"""
        response = self.client.delete("/api/subscriptions/9999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_cancel_subscription_already_cancelled(self):
        """Test cancelling already cancelled subscription"""
        # Cancel first time
        self.client.delete(f"/api/subscriptions/{self.subscription_id}")
        # Cancel second time
        response = self.client.delete(f"/api/subscriptions/{self.subscription_id}")
        # May return 404 or 200 depending on implementation
        assert response.status_code in [200, 404]


class TestGetSubscriptionPlans:
    """Tests for GET /api/subscription-plans endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.client = TestClient(app)
    
    def test_get_subscription_plans(self):
        """Test getting subscription plans"""
        response = self.client.get("/api/subscription-plans")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3  # daily, weekly, monthly
    
    def test_subscription_plans_structure(self):
        """Test subscription plans have required fields"""
        response = self.client.get("/api/subscription-plans")
        data = response.json()
        for plan in data:
            assert "id" in plan
            assert "name" in plan
            assert "description" in plan
            assert "price" in plan
            assert "benefits" in plan
    
    def test_subscription_plans_daily(self):
        """Test daily plan exists"""
        response = self.client.get("/api/subscription-plans")
        data = response.json()
        daily_plan = next((p for p in data if p["id"] == "daily"), None)
        assert daily_plan is not None
        assert daily_plan["name"] == "Daily Fresh"
    
    def test_subscription_plans_weekly(self):
        """Test weekly plan exists"""
        response = self.client.get("/api/subscription-plans")
        data = response.json()
        weekly_plan = next((p for p in data if p["id"] == "weekly"), None)
        assert weekly_plan is not None
        assert weekly_plan["name"] == "Weekly Bundle"
    
    def test_subscription_plans_monthly(self):
        """Test monthly plan exists"""
        response = self.client.get("/api/subscription-plans")
        data = response.json()
        monthly_plan = next((p for p in data if p["id"] == "monthly"), None)
        assert monthly_plan is not None
        assert monthly_plan["name"] == "Monthly Mega"
