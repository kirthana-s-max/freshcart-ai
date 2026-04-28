"""
Store Unit Tests
=================
Tests for data store classes: UserStore, ProductStore, OrderStore, etc.
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import UserStore, ProductStore, OrderStore, SubscriptionStore, NotificationStore


class TestUserStore:
    """Tests for UserStore class"""
    
    @pytest.fixture
    def user_store(self):
        """Create fresh UserStore for each test"""
        return UserStore()
    
    def test_create_user(self, user_store):
        """Test creating a new user"""
        user = user_store.create_user(
            name="Test User",
            email="test@example.com",
            phone="+91 9876543210",
            address="123 Test St",
            password="password123"
        )
        assert user["name"] == "Test User"
        assert user["email"] == "test@example.com"
        assert "id" in user
        assert "password" in user
        assert user["password"] != "password123"  # Password should be hashed
    
    def test_create_duplicate_email(self, user_store):
        """Test creating user with duplicate email fails"""
        user_store.create_user(
            name="User 1",
            email="duplicate@test.com",
            phone="123",
            address="Address",
            password="pass1"
        )
        with pytest.raises(ValueError, match="already registered"):
            user_store.create_user(
                name="User 2",
                email="duplicate@test.com",
                phone="456",
                address="Address 2",
                password="pass2"
            )
    
    def test_authenticate_valid(self, user_store):
        """Test authenticating with valid credentials"""
        user_store.create_user(
            name="Test User",
            email="auth@test.com",
            phone="123",
            address="Address",
            password="correctpassword"
        )
        result = user_store.authenticate("auth@test.com", "correctpassword")
        assert result is not None
        assert "user" in result
        assert "token" in result
    
    def test_authenticate_invalid_email(self, user_store):
        """Test authenticating with non-existent email"""
        result = user_store.authenticate("nonexistent@test.com", "password")
        assert result is None
    
    def test_authenticate_invalid_password(self, user_store):
        """Test authenticating with wrong password"""
        user_store.create_user(
            name="Test User",
            email="wrongpass@test.com",
            phone="123",
            address="Address",
            password="correctpassword"
        )
        result = user_store.authenticate("wrongpass@test.com", "wrongpassword")
        assert result is None
    
    def test_get_user_by_token(self, user_store):
        """Test getting user by token"""
        user_store.create_user(
            name="Test User",
            email="token@test.com",
            phone="123",
            address="Address",
            password="password"
        )
        result = user_store.authenticate("token@test.com", "password")
        token = result["token"]
        user = user_store.get_user(token)
        assert user is not None
        assert user["email"] == "token@test.com"
    
    def test_get_user_invalid_token(self, user_store):
        """Test getting user with invalid token"""
        user = user_store.get_user("invalid-token")
        assert user is None


class TestProductStore:
    """Tests for ProductStore class"""
    
    @pytest.fixture
    def product_store(self):
        """Create ProductStore instance"""
        return ProductStore()
    
    def test_get_all_products(self, product_store):
        """Test getting all products"""
        products = product_store.get_all()
        assert isinstance(products, list)
        assert len(products) > 0
    
    def test_get_product_by_id(self, product_store):
        """Test getting product by ID"""
        product = product_store.get_by_id(1)
        assert product is not None
        assert product["id"] == 1
        assert "name" in product
    
    def test_get_product_invalid_id(self, product_store):
        """Test getting product with invalid ID"""
        product = product_store.get_by_id(9999)
        assert product is None
    
    def test_get_products_by_category(self, product_store):
        """Test filtering products by category"""
        vegetables = product_store.get_by_category("vegetables")
        assert isinstance(vegetables, list)
        for p in vegetables:
            assert p["category"].lower() == "vegetables"
    
    def test_category_case_insensitive(self, product_store):
        """Test category filter is case insensitive"""
        v1 = product_store.get_by_category("VEGETABLES")
        v2 = product_store.get_by_category("vegetables")
        assert len(v1) == len(v2)
    
    def test_search_products(self, product_store):
        """Test searching products"""
        results = product_store.search("tomato")
        assert isinstance(results, list)
        for p in results:
            assert "tomato" in p["name"].lower()
    
    def test_search_case_insensitive(self, product_store):
        """Test search is case insensitive"""
        r1 = product_store.search("TOMATO")
        r2 = product_store.search("tomato")
        assert len(r1) == len(r2)
    
    def test_get_categories(self, product_store):
        """Test getting all categories"""
        categories = product_store.get_categories()
        assert isinstance(categories, list)
        assert "vegetables" in categories
        assert "fruits" in categories
        assert "nuts" in categories


class TestOrderStore:
    """Tests for OrderStore class"""
    
    @pytest.fixture
    def order_store(self):
        """Create fresh OrderStore for each test"""
        return OrderStore()
    
    def test_create_order(self, order_store):
        """Test creating an order"""
        order = order_store.create(
            user_id=1,
            items=[{"product_id": 1, "name": "Test", "price": 5.99, "quantity": 2}],
            subtotal=11.98,
            delivery_fee=2.99,
            total=14.97,
            address="123 Test St",
            payment_method="cod"
        )
        assert order["id"] == 1
        assert order["status"] == "confirmed"
        assert len(order["items"]) == 1
    
    def test_get_order(self, order_store):
        """Test getting order by ID"""
        order_store.create(
            user_id=1,
            items=[{"product_id": 1, "name": "Test", "price": 5.99, "quantity": 1}],
            subtotal=5.99,
            delivery_fee=2.99,
            total=8.98,
            address="Address",
            payment_method="cod"
        )
        order = order_store.get(1)
        assert order is not None
        assert order["id"] == 1
    
    def test_get_order_invalid_id(self, order_store):
        """Test getting order with invalid ID"""
        order = order_store.get(9999)
        assert order is None
    
    def test_get_all_orders(self, order_store):
        """Test getting all orders"""
        order_store.create(
            user_id=1,
            items=[{"product_id": 1, "name": "Test", "price": 5.99, "quantity": 1}],
            subtotal=5.99,
            delivery_fee=2.99,
            total=8.98,
            address="Address",
            payment_method="cod"
        )
        orders = order_store.get_all()
        assert isinstance(orders, list)
        assert len(orders) == 1
    
    def test_get_user_orders(self, order_store):
        """Test getting orders for specific user"""
        order_store.create(
            user_id=1,
            items=[{"product_id": 1, "name": "Test", "price": 5.99, "quantity": 1}],
            subtotal=5.99,
            delivery_fee=2.99,
            total=8.98,
            address="Address",
            payment_method="cod"
        )
        user_orders = order_store.get_user_orders(1)
        assert len(user_orders) == 1
        
        other_user_orders = order_store.get_user_orders(999)
        assert len(other_user_orders) == 0


class TestSubscriptionStore:
    """Tests for SubscriptionStore class"""
    
    @pytest.fixture
    def subscription_store(self):
        """Create fresh SubscriptionStore for each test"""
        return SubscriptionStore()
    
    def test_create_subscription(self, subscription_store):
        """Test creating a subscription"""
        sub = subscription_store.create(
            user_id=1,
            product_id=1,
            product_name="Organic Tomatoes",
            frequency="weekly",
            quantity=2,
            price=3.99
        )
        assert sub["id"] == 1
        assert sub["frequency"] == "weekly"
        assert sub["quantity"] == 2
        assert sub["active"] is True
        assert "next_delivery" in sub
    
    def test_create_daily_subscription(self, subscription_store):
        """Test creating daily subscription calculates next delivery"""
        sub = subscription_store.create(
            user_id=1,
            product_id=1,
            product_name="Test",
            frequency="daily",
            quantity=1,
            price=5.99
        )
        assert sub["frequency"] == "daily"
    
    def test_create_monthly_subscription(self, subscription_store):
        """Test creating monthly subscription"""
        sub = subscription_store.create(
            user_id=1,
            product_id=1,
            product_name="Test",
            frequency="monthly",
            quantity=1,
            price=5.99
        )
        assert sub["frequency"] == "monthly"
    
    def test_get_user_subscriptions(self, subscription_store):
        """Test getting user's subscriptions"""
        subscription_store.create(
            user_id=1,
            product_id=1,
            product_name="Test",
            frequency="weekly",
            quantity=1,
            price=5.99
        )
        subs = subscription_store.get_user_subscriptions(1)
        assert len(subs) == 1
    
    def test_cancel_subscription(self, subscription_store):
        """Test cancelling a subscription"""
        subscription_store.create(
            user_id=1,
            product_id=1,
            product_name="Test",
            frequency="weekly",
            quantity=1,
            price=5.99
        )
        result = subscription_store.cancel(1)
        assert result is True
        
        subs = subscription_store.get_user_subscriptions(1)
        assert len(subs) == 0  # Cancelled subscription not returned
    
    def test_cancel_invalid_subscription(self, subscription_store):
        """Test cancelling non-existent subscription"""
        result = subscription_store.cancel(9999)
        assert result is False


class TestNotificationStore:
    """Tests for NotificationStore class"""
    
    @pytest.fixture
    def notification_store(self):
        """Create fresh NotificationStore for each test"""
        return NotificationStore()
    
    def test_create_notification(self, notification_store):
        """Test creating a notification"""
        notif = notification_store.create(
            user_id=1,
            notification_type="order",
            title="Test Notification",
            message="This is a test",
            data={"order_id": 1}
        )
        assert notif["id"] == 1
        assert notif["title"] == "Test Notification"
        assert notif["read"] is False
    
    def test_get_user_notifications(self, notification_store):
        """Test getting user's notifications"""
        notification_store.create(
            user_id=1,
            notification_type="order",
            title="Notif 1",
            message="Message 1"
        )
        notification_store.create(
            user_id=1,
            notification_type="delivery",
            title="Notif 2",
            message="Message 2"
        )
        notifs = notification_store.get_user_notifications(1)
        assert len(notifs) == 2
    
    def test_get_unread_count(self, notification_store):
        """Test getting unread notification count"""
        notification_store.create(
            user_id=1,
            notification_type="order",
            title="Notif 1",
            message="Message"
        )
        notification_store.create(
            user_id=1,
            notification_type="delivery",
            title="Notif 2",
            message="Message"
        )
        count = notification_store.get_unread_count(1)
        assert count == 2
    
    def test_mark_as_read(self, notification_store):
        """Test marking notification as read"""
        notif = notification_store.create(
            user_id=1,
            notification_type="order",
            title="Test",
            message="Test"
        )
        result = notification_store.mark_as_read(1)
        assert result is True
        assert notification_store._notifications[1]["read"] is True
    
    def test_mark_all_as_read(self, notification_store):
        """Test marking all notifications as read"""
        notification_store.create(user_id=1, notification_type="order", title="N1", message="M")
        notification_store.create(user_id=1, notification_type="order", title="N2", message="M")
        count = notification_store.mark_all_as_read(1)
        assert count == 2
    
    def test_delete_notification(self, notification_store):
        """Test deleting a notification"""
        notification_store.create(
            user_id=1,
            notification_type="order",
            title="Test",
            message="Test"
        )
        result = notification_store.delete(1)
        assert result is True
        assert 1 not in notification_store._notifications
    
    def test_delete_invalid_notification(self, notification_store):
        """Test deleting non-existent notification"""
        result = notification_store.delete(9999)
        assert result is False
    
    def test_create_order_notification(self, notification_store):
        """Test creating order notification"""
        notif = notification_store.create_order_notification(
            user_id=1,
            order_id=123,
            items=[{"name": "Tomato", "quantity": 2}]
        )
        assert notif["type"] == "order"
        assert "123" in notif["message"]
