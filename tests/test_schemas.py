"""
Pydantic Schema Validation Tests
================================
Tests for all Pydantic models in api/models/schemas.py
"""

import pytest
from pydantic import ValidationError
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.models.schemas import (
    SubscriptionFrequency,
    OrderStatus,
    UserBase,
    UserCreate,
    User,
    ProductBase,
    Product,
    CartItem,
    CartResponse,
    SubscriptionCreate,
    Subscription,
    OrderItem,
    OrderCreate,
    Order,
    LoginRequest,
    AuthResponse,
)


class TestSubscriptionFrequency:
    """Tests for SubscriptionFrequency enum"""
    
    def test_daily_frequency(self):
        """Test daily frequency value"""
        assert SubscriptionFrequency.DAILY.value == "daily"
    
    def test_weekly_frequency(self):
        """Test weekly frequency value"""
        assert SubscriptionFrequency.WEEKLY.value == "weekly"
    
    def test_monthly_frequency(self):
        """Test monthly frequency value"""
        assert SubscriptionFrequency.MONTHLY.value == "monthly"
    
    def test_frequency_as_string(self):
        """Test frequency can be used as string"""
        assert str(SubscriptionFrequency.DAILY) == "SubscriptionFrequency.DAILY"


class TestOrderStatus:
    """Tests for OrderStatus enum"""
    
    def test_all_statuses_defined(self):
        """Test all order statuses are defined"""
        assert OrderStatus.PENDING.value == "pending"
        assert OrderStatus.CONFIRMED.value == "confirmed"
        assert OrderStatus.PREPARING.value == "preparing"
        assert OrderStatus.OUT_FOR_DELIVERY.value == "out_for_delivery"
        assert OrderStatus.DELIVERED.value == "delivered"
        assert OrderStatus.CANCELLED.value == "cancelled"


class TestLoginRequest:
    """Tests for LoginRequest model"""
    
    def test_valid_login_request(self):
        """Test valid login credentials"""
        login = LoginRequest(email="user@test.com", password="password123")
        assert login.email == "user@test.com"
        assert login.password == "password123"
    
    def test_login_missing_email(self):
        """Test login with missing email raises error"""
        with pytest.raises(ValidationError):
            LoginRequest(password="password123")
    
    def test_login_missing_password(self):
        """Test login with missing password raises error"""
        with pytest.raises(ValidationError):
            LoginRequest(email="user@test.com")
    
    def test_login_empty_email(self):
        """Test login with empty email - Pydantic allows empty strings by default"""
        # Empty string is valid for email field in current implementation
        login = LoginRequest(email="", password="password123")
        assert login.email == ""
    
    def test_login_empty_password(self):
        """Test login with empty password - Pydantic allows empty strings by default"""
        # Empty string is valid for password field in current implementation
        login = LoginRequest(email="user@test.com", password="")
        assert login.password == ""


class TestUserCreate:
    """Tests for UserCreate model"""
    
    def test_valid_user_create(self):
        """Test valid user creation data"""
        user = UserCreate(
            name="John Doe",
            email="john@test.com",
            phone="+91 9876543210",
            address="123 Main St, Mumbai"
        )
        assert user.name == "John Doe"
        assert user.email == "john@test.com"
        assert user.phone == "+91 9876543210"
        assert user.address == "123 Main St, Mumbai"
    
    def test_user_create_missing_name(self):
        """Test user creation without name raises error"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="john@test.com",
                phone="+91 9876543210",
                address="123 Main St"
            )
    
    def test_user_create_missing_email(self):
        """Test user creation without email raises error"""
        with pytest.raises(ValidationError):
            UserCreate(
                name="John Doe",
                phone="+91 9876543210",
                address="123 Main St"
            )
    
    def test_user_create_missing_phone(self):
        """Test user creation without phone raises error"""
        with pytest.raises(ValidationError):
            UserCreate(
                name="John Doe",
                email="john@test.com",
                address="123 Main St"
            )
    
    def test_user_create_missing_address(self):
        """Test user creation without address raises error"""
        with pytest.raises(ValidationError):
            UserCreate(
                name="John Doe",
                email="john@test.com",
                phone="+91 9876543210"
            )


class TestProduct:
    """Tests for Product model"""
    
    def test_valid_product(self, sample_product):
        """Test valid product creation"""
        product_data = sample_product.copy()
        product_data["id"] = 1
        product = Product(**product_data)
        assert product.id == 1
        assert product.name == "Organic Tomatoes"
        assert product.price == 3.99
        assert product.category == "vegetables"
        assert product.stock == 100
    
    def test_product_with_optional_image(self, sample_product):
        """Test product with optional image URL"""
        product_data = sample_product.copy()
        product_data["id"] = 1
        product_data["image_url"] = "https://example.com/image.jpg"
        product = Product(**product_data)
        assert product.image_url == "https://example.com/image.jpg"
    
    def test_product_missing_required_field(self):
        """Test product with missing required field raises error"""
        with pytest.raises(ValidationError):
            Product(id=1, name="Tomato", category="vegetables")
    
    def test_product_negative_price(self):
        """Test product with negative price - currently allowed by model"""
        # Model doesn't validate negative prices
        product = Product(
            id=1,
            name="Tomato",
            category="vegetables",
            price=-5.99,
            unit="kg",
            stock=100,
            description="Test"
        )
        assert product.price == -5.99
    
    def test_product_zero_price(self):
        """Test product with zero price is valid"""
        product = Product(
            id=1,
            name="Free Sample",
            category="vegetables",
            price=0.0,
            unit="piece",
            stock=10,
            description="Free sample product"
        )
        assert product.price == 0.0
    
    def test_product_negative_stock(self):
        """Test product with negative stock - currently allowed by model"""
        # Model doesn't validate negative stock
        product = Product(
            id=1,
            name="Tomato",
            category="vegetables",
            price=3.99,
            unit="kg",
            stock=-10,
            description="Test"
        )
        assert product.stock == -10


class TestCartItem:
    """Tests for CartItem model"""
    
    def test_valid_cart_item(self):
        """Test valid cart item"""
        item = CartItem(
            product_id=1,
            name="Organic Tomatoes",
            price=3.99,
            quantity=2,
            unit="kg",
            subtotal=7.98
        )
        assert item.product_id == 1
        assert item.quantity == 2
        assert item.subtotal == 7.98
    
    def test_cart_item_integer_quantity(self):
        """Test cart item with integer quantity"""
        item = CartItem(
            product_id=1,
            name="Test",
            price=1.0,
            quantity=5,
            unit="kg",
            subtotal=5.0
        )
        assert item.quantity == 5
    
    def test_cart_item_missing_required_field(self):
        """Test cart item with missing required field raises error"""
        with pytest.raises(ValidationError):
            CartItem(
                product_id=1,
                name="Test",
                price=1.0,
                unit="kg",
                subtotal=1.0
            )
    
    def test_cart_item_zero_quantity(self):
        """Test cart item with zero quantity is valid"""
        item = CartItem(
            product_id=1,
            name="Test",
            price=1.0,
            quantity=0,
            unit="kg",
            subtotal=0.0
        )
        assert item.quantity == 0


class TestCartResponse:
    """Tests for CartResponse model"""
    
    def test_valid_cart_response(self):
        """Test valid cart response"""
        items = [
            CartItem(
                product_id=1,
                name="Tomato",
                price=3.99,
                quantity=2,
                unit="kg",
                subtotal=7.98
            )
        ]
        response = CartResponse(
            items=items,
            subtotal=7.98,
            delivery_fee=2.99,
            total=10.97
        )
        assert len(response.items) == 1
        assert response.total == 10.97
    
    def test_empty_cart_response(self):
        """Test empty cart response"""
        response = CartResponse(
            items=[],
            subtotal=0.0,
            delivery_fee=0.0,
            total=0.0
        )
        assert len(response.items) == 0
        assert response.total == 0.0
    
    def test_cart_response_missing_items(self):
        """Test cart response without items raises error"""
        with pytest.raises(ValidationError):
            CartResponse(
                subtotal=0.0,
                delivery_fee=0.0,
                total=0.0
            )


class TestSubscriptionCreate:
    """Tests for SubscriptionCreate model"""
    
    def test_valid_subscription_daily(self):
        """Test valid daily subscription"""
        sub = SubscriptionCreate(
            product_id=1,
            frequency=SubscriptionFrequency.DAILY,
            quantity=2
        )
        assert sub.frequency == SubscriptionFrequency.DAILY
        assert sub.quantity == 2
    
    def test_valid_subscription_weekly(self):
        """Test valid weekly subscription"""
        sub = SubscriptionCreate(
            product_id=1,
            frequency=SubscriptionFrequency.WEEKLY
        )
        assert sub.frequency == SubscriptionFrequency.WEEKLY
    
    def test_valid_subscription_monthly(self):
        """Test valid monthly subscription"""
        sub = SubscriptionCreate(
            product_id=1,
            frequency=SubscriptionFrequency.MONTHLY,
            quantity=5
        )
        assert sub.frequency == SubscriptionFrequency.MONTHLY
        assert sub.quantity == 5
    
    def test_subscription_default_quantity(self):
        """Test subscription default quantity is 1"""
        sub = SubscriptionCreate(
            product_id=1,
            frequency=SubscriptionFrequency.WEEKLY
        )
        assert sub.quantity == 1
    
    def test_subscription_missing_product_id(self):
        """Test subscription without product_id raises error"""
        with pytest.raises(ValidationError):
            SubscriptionCreate(frequency=SubscriptionFrequency.DAILY)
    
    def test_subscription_missing_frequency(self):
        """Test subscription without frequency raises error"""
        with pytest.raises(ValidationError):
            SubscriptionCreate(product_id=1)
    
    def test_subscription_invalid_frequency(self):
        """Test subscription with invalid frequency raises error"""
        with pytest.raises(ValidationError):
            SubscriptionCreate(product_id=1, frequency="invalid")
    
    def test_subscription_negative_quantity(self):
        """Test subscription with negative quantity - currently allowed by model"""
        # Model doesn't validate negative quantity
        sub = SubscriptionCreate(
            product_id=1,
            frequency=SubscriptionFrequency.DAILY,
            quantity=-1
        )
        assert sub.quantity == -1
    
    def test_subscription_zero_quantity(self):
        """Test subscription with zero quantity - currently allowed by model"""
        # Model doesn't validate zero quantity
        sub = SubscriptionCreate(
            product_id=1,
            frequency=SubscriptionFrequency.DAILY,
            quantity=0
        )
        assert sub.quantity == 0


class TestOrderCreate:
    """Tests for OrderCreate model"""
    
    def test_valid_order_create(self, sample_order_items, sample_address):
        """Test valid order creation"""
        order = OrderCreate(
            items=sample_order_items,
            address=sample_address
        )
        assert len(order.items) == 2
        assert order.address == sample_address
        assert order.payment_method == "cod"
    
    def test_order_create_with_card_payment(self, sample_order_items, sample_address):
        """Test order with card payment"""
        order = OrderCreate(
            items=sample_order_items,
            address=sample_address,
            payment_method="card"
        )
        assert order.payment_method == "card"
    
    def test_order_create_empty_items(self, sample_address):
        """Test order with empty items list"""
        order = OrderCreate(
            items=[],
            address=sample_address
        )
        assert len(order.items) == 0
    
    def test_order_create_missing_address(self, sample_order_items):
        """Test order without address raises error"""
        with pytest.raises(ValidationError):
            OrderCreate(items=sample_order_items)
    
    def test_order_create_missing_items(self, sample_address):
        """Test order without items raises error"""
        with pytest.raises(ValidationError):
            OrderCreate(address=sample_address)


class TestOrderItem:
    """Tests for OrderItem model"""
    
    def test_valid_order_item(self):
        """Test valid order item"""
        item = OrderItem(
            product_id=1,
            name="Organic Tomatoes",
            price=3.99,
            quantity=2,
            subtotal=7.98
        )
        assert item.product_id == 1
        assert item.quantity == 2
        assert item.subtotal == 7.98
    
    def test_order_item_missing_field(self):
        """Test order item with missing field raises error"""
        with pytest.raises(ValidationError):
            OrderItem(
                product_id=1,
                name="Tomato",
                price=3.99,
                quantity=2
            )


class TestAuthResponse:
    """Tests for AuthResponse model"""
    
    def test_valid_auth_response(self):
        """Test valid auth response"""
        response = AuthResponse(
            user={"id": 1, "name": "Test User"},
            token="test-token-123"
        )
        assert response.token == "test-token-123"
        assert response.user["id"] == 1
    
    def test_auth_response_missing_token(self):
        """Test auth response without token raises error"""
        with pytest.raises(ValidationError):
            AuthResponse(user={"id": 1})
    
    def test_auth_response_missing_user(self):
        """Test auth response without user raises error"""
        with pytest.raises(ValidationError):
            AuthResponse(token="test-token")
