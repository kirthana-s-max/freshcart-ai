"""
FreshCart AI - Agent System
===========================
This module defines all AI agents used in the FreshCart e-commerce platform.
Each agent is responsible for a specific domain of functionality.
"""

import pandas as pd
import random
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum


# ==================== PRODUCT AGENT ====================

class ProductAgent:
    """
    Agent responsible for product catalog management.
    Handles loading, searching, and filtering products from CSV storage.
    """
    
    def __init__(self, csv_path: str = "data/products.csv"):
        self.csv_path = Path(csv_path)
        self._products = None
    
    def _load_products(self) -> pd.DataFrame:
        """Load products from CSV file (cached)"""
        if self._products is None:
            self._products = pd.read_csv(self.csv_path)
        return self._products
    
    def get_all_products(self) -> List[dict]:
        """Get all products from catalog"""
        df = self._load_products()
        return df.to_dict('records')
    
    def get_products_by_category(self, category: str) -> List[dict]:
        """Get products filtered by category (vegetables, fruits, nuts)"""
        df = self._load_products()
        filtered = df[df['category'].str.lower() == category.lower()]
        return filtered.to_dict('records')
    
    def search_products(self, keyword: str) -> List[dict]:
        """Search products by name, category, or description"""
        df = self._load_products()
        keyword_lower = keyword.lower()
        filtered = df[
            df['name'].str.lower().str.contains(keyword_lower, na=False) |
            df['category'].str.lower().str.contains(keyword_lower, na=False) |
            df['description'].str.lower().str.contains(keyword_lower, na=False)
        ]
        return filtered.to_dict('records')
    
    def get_product_by_id(self, product_id: int) -> Optional[dict]:
        """Get a single product by ID"""
        df = self._load_products()
        product = df[df['id'] == product_id]
        if product.empty:
            return None
        return product.iloc[0].to_dict()
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        df = self._load_products()
        return df['category'].unique().tolist()
    
    def get_low_stock_products(self, threshold: int = 10) -> List[dict]:
        """Get products with stock below threshold"""
        df = self._load_products()
        low_stock = df[df['stock'] < threshold]
        return low_stock.to_dict('records')


# ==================== CART AGENT ====================

class CartItem:
    """Represents an item in the shopping cart"""
    
    def __init__(self, product_id: int, name: str, price: float, quantity: int, unit: str):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.unit = unit
    
    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "unit": self.unit,
            "subtotal": self.price * self.quantity
        }


class CartAgent:
    """
    Agent responsible for shopping cart operations.
    Manages cart items, quantities, and total calculations.
    """
    
    DELIVERY_FEE = 2.99
    
    def __init__(self):
        self._cart: Dict[int, CartItem] = {}
    
    def add_item(self, product_id: int, name: str, price: float, quantity: int = 1, unit: str = "") -> Dict:
        """Add item to cart or increase quantity if exists"""
        if product_id in self._cart:
            self._cart[product_id].quantity += quantity
        else:
            self._cart[product_id] = CartItem(product_id, name, price, quantity, unit)
        return self._cart[product_id].to_dict()
    
    def remove_item(self, product_id: int) -> bool:
        """Remove item from cart"""
        if product_id in self._cart:
            del self._cart[product_id]
            return True
        return False
    
    def update_quantity(self, product_id: int, quantity: int) -> Optional[Dict]:
        """Update item quantity (set to 0 to remove)"""
        if product_id not in self._cart:
            return None
        if quantity <= 0:
            return self.remove_item(product_id)
        self._cart[product_id].quantity = quantity
        return self._cart[product_id].to_dict()
    
    def view_cart(self) -> List[Dict]:
        """Get all items in cart"""
        return [item.to_dict() for item in self._cart.values()]
    
    def calculate_total(self) -> Dict:
        """Calculate subtotal, delivery fee, and total"""
        items = self.view_cart()
        subtotal = sum(item['subtotal'] for item in items)
        delivery_fee = self.DELIVERY_FEE if items else 0
        total = subtotal + delivery_fee
        return {
            "items": items,
            "subtotal": round(subtotal, 2),
            "delivery_fee": delivery_fee,
            "total": round(total, 2),
            "item_count": len(items)
        }
    
    def clear_cart(self):
        """Empty the cart"""
        self._cart.clear()
    
    def get_cart_count(self) -> int:
        """Get total number of items in cart"""
        return sum(item.quantity for item in self._cart.values())
    
    def is_empty(self) -> bool:
        """Check if cart is empty"""
        return len(self._cart) == 0


# ==================== ORDER AGENT ====================

class OrderItem:
    """Represents an item in an order"""
    
    def __init__(self, product_id: int, name: str, price: float, quantity: int, unit: str = ""):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.unit = unit
    
    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "unit": self.unit,
            "subtotal": self.price * self.quantity
        }


class Order:
    """Represents a customer order"""
    
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_PREPARING = "preparing"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"
    
    def __init__(self, order_id: int, items: List[Dict], total: float, address: str = "", user_id: int = None):
        self.id = order_id
        self.user_id = user_id
        self.items = [
            OrderItem(
                product_id=item['product_id'],
                name=item['name'],
                price=item['price'],
                quantity=item['quantity'],
                unit=item.get('unit', '')
            ) if isinstance(item, dict) else item
            for item in items
        ]
        self.total = total
        self.address = address
        self.created_at = datetime.now()
        self.status = self.STATUS_CONFIRMED
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "items": [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.items],
            "total": self.total,
            "address": self.address,
            "created_at": self.created_at.isoformat(),
            "status": self.status
        }


class OrderAgent:
    """
    Agent responsible for order processing.
    Manages order creation, tracking, and history.
    """
    
    def __init__(self):
        self._orders: Dict[int, Order] = {}
        self._next_id = 1
    
    def place_order(self, items: List[Dict], total: float, address: str = "") -> Dict:
        """Create a new order"""
        order = Order(order_id=self._next_id, items=items, total=total, address=address)
        self._orders[self._next_id] = order
        self._next_id += 1
        return order.to_dict()
    
    def get_order_history(self) -> List[Dict]:
        """Get all orders"""
        return [order.to_dict() for order in self._orders.values()]
    
    def get_user_orders(self, user_id: int) -> List[Dict]:
        """Get orders for a specific user"""
        return [
            order.to_dict() for order in self._orders.values()
            if order.user_id == user_id
        ]
    
    def get_order_by_id(self, order_id: int) -> Optional[Dict]:
        """Get a specific order by ID"""
        if order_id in self._orders:
            return self._orders[order_id].to_dict()
        return None
    
    def update_status(self, order_id: int, status: str) -> bool:
        """Update order status"""
        if order_id in self._orders:
            self._orders[order_id].status = status
            return True
        return False
    
    def cancel_order(self, order_id: int) -> bool:
        """Cancel an order"""
        if order_id in self._orders:
            self._orders[order_id].status = Order.STATUS_CANCELLED
            return True
        return False


# ==================== SUBSCRIPTION AGENT ====================

class SubscriptionFrequency(Enum):
    """Valid subscription frequencies"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Subscription:
    """Represents a product subscription"""
    
    def __init__(self, subscription_id: int, product_id: int, product_name: str,
                 frequency: str, quantity: int, price: float):
        self.id = subscription_id
        self.product_id = product_id
        self.product_name = product_name
        self.frequency = frequency
        self.quantity = quantity
        self.price = price
        self.created_at = datetime.now()
        self.active = True
    
    def to_dict(self) -> dict:
        days = {"daily": 1, "weekly": 7, "monthly": 30}.get(self.frequency, 7)
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "frequency": self.frequency,
            "quantity": self.quantity,
            "price": self.price,
            "total": self.price * self.quantity,
            "next_delivery": (datetime.now() + timedelta(days=days)).isoformat(),
            "active": self.active,
            "created_at": self.created_at.isoformat()
        }


class SubscriptionAgent:
    """
    Agent responsible for subscription management.
    Handles recurring deliveries with configurable frequencies.
    """
    
    def __init__(self):
        self._subscriptions: Dict[int, Subscription] = {}
        self._next_id = 1
    
    def create_subscription(self, product_id: int, product_name: str,
                           frequency: str, quantity: int, price: float) -> Dict:
        """Create a new subscription"""
        valid_frequencies = [f.value for f in SubscriptionFrequency]
        if frequency.lower() not in valid_frequencies:
            raise ValueError(f"Invalid frequency. Must be one of: {valid_frequencies}")
        
        subscription = Subscription(
            subscription_id=self._next_id,
            product_id=product_id,
            product_name=product_name,
            frequency=frequency.lower(),
            quantity=quantity,
            price=price
        )
        self._subscriptions[self._next_id] = subscription
        self._next_id += 1
        return subscription.to_dict()
    
    def get_active_subscriptions(self) -> List[Dict]:
        """Get all active subscriptions"""
        return [sub.to_dict() for sub in self._subscriptions.values() if sub.active]
    
    def get_user_subscriptions(self, user_id: int) -> List[Dict]:
        """Get active subscriptions for a user"""
        return [
            sub.to_dict() for sub in self._subscriptions.values()
            if sub.user_id == user_id and sub.active
        ]
    
    def get_all_subscriptions(self) -> List[Dict]:
        """Get all subscriptions (active and inactive)"""
        return [sub.to_dict() for sub in self._subscriptions.values()]
    
    def cancel_subscription(self, subscription_id: int) -> bool:
        """Cancel a subscription"""
        if subscription_id in self._subscriptions:
            self._subscriptions[subscription_id].active = False
            return True
        return False
    
    def reactivate_subscription(self, subscription_id: int) -> bool:
        """Reactivate a cancelled subscription"""
        if subscription_id in self._subscriptions:
            self._subscriptions[subscription_id].active = True
            return True
        return False
    
    def get_subscription_by_id(self, subscription_id: int) -> Optional[Dict]:
        """Get subscription details by ID"""
        if subscription_id in self._subscriptions:
            return self._subscriptions[subscription_id].to_dict()
        return None


# ==================== RECOMMENDATION AGENT ====================

class RecommendationAgent:
    """
    Agent responsible for product recommendations.
    Uses collaborative filtering and category-based suggestions.
    """
    
    def __init__(self, product_agent: ProductAgent):
        self.product_agent = product_agent
    
    def recommend_by_product(self, product_id: int) -> List[Dict]:
        """Get recommendations based on a specific product"""
        product = self.product_agent.get_product_by_id(product_id)
        if not product:
            return []
        return self.recommend_by_category(product['category'])
    
    def recommend_by_category(self, category: str, limit: int = 5) -> List[Dict]:
        """Get recommendations from same category"""
        products = self.product_agent.get_products_by_category(category)
        if len(products) <= limit:
            return products
        return random.sample(products, limit)
    
    def get_popular_products(self, limit: int = 10) -> List[Dict]:
        """Get popular products (random selection for demo)"""
        all_products = self.product_agent.get_all_products()
        if len(all_products) <= limit:
            return all_products
        return random.sample(all_products, limit)
    
    def get_complementary_products(self, product_id: int) -> List[Dict]:
        """Get complementary products from related categories"""
        product = self.product_agent.get_product_by_id(product_id)
        if not product:
            return []
        
        complementary_map = {
            'vegetables': 'fruits',
            'fruits': 'nuts',
            'nuts': 'vegetables'
        }
        related_category = complementary_map.get(product['category'], 'vegetables')
        return self.recommend_by_category(related_category, limit=3)
    
    def get_bundle_suggestions(self, cart_items: List[Dict]) -> List[Dict]:
        """Suggest products to complete a meal bundle"""
        categories = set(item.get('category', '') for item in cart_items)
        suggestions = []
        for category in ['vegetables', 'fruits', 'nuts']:
            if category not in categories:
                products = self.product_agent.get_products_by_category(category)
                if products:
                    suggestions.append(random.choice(products))
        return suggestions


# ==================== NOTIFICATION AGENT ====================

class NotificationType(Enum):
    """Types of notifications"""
    ORDER = "order"
    DELIVERY = "delivery"
    SUBSCRIPTION = "subscription"
    PRODUCT = "product"
    PROMO = "promo"


class Notification:
    """Represents a user notification"""
    
    def __init__(self, notification_id: int, user_id: int, notification_type: str,
                 title: str, message: str, data: dict = None):
        self.id = notification_id
        self.user_id = user_id
        self.type = notification_type
        self.title = title
        self.message = message
        self.data = data or {}
        self.read = False
        self.created_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "data": self.data,
            "read": self.read,
            "created_at": self.created_at.isoformat()
        }


class NotificationAgent:
    """
    Agent responsible for user notifications.
    Handles order confirmations, delivery updates, and alerts.
    """
    
    def __init__(self):
        self._notifications: Dict[int, Notification] = {}
        self._next_id = 1
    
    def create_notification(self, user_id: int, notification_type: str,
                            title: str, message: str, data: dict = None) -> Dict:
        """Create a new notification"""
        notification = Notification(
            notification_id=self._next_id,
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            data=data
        )
        self._notifications[self._next_id] = notification
        self._next_id += 1
        return notification.to_dict()
    
    def create_order_notification(self, user_id: int, order_id: int, items: List[Dict]) -> Dict:
        """Create order confirmation notification"""
        item_names = [item.get('name', 'Item') for item in items[:3]]
        items_text = ", ".join(item_names)
        if len(items) > 3:
            items_text += f" and {len(items) - 3} more"
        
        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.ORDER.value,
            title="Order Confirmed!",
            message=f"Your order #{order_id} ({items_text}) has been placed successfully.",
            data={"order_id": order_id}
        )
    
    def create_delivery_notification(self, user_id: int, order_id: int,
                                     status: str, message: str) -> Dict:
        """Create delivery status notification"""
        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.DELIVERY.value,
            title=f"Delivery Update - Order #{order_id}",
            message=message,
            data={"order_id": order_id, "status": status}
        )
    
    def create_subscription_notification(self, user_id: int, subscription_id: int,
                                       product_name: str, action: str) -> Dict:
        """Create subscription-related notification"""
        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.SUBSCRIPTION.value,
            title=f"Subscription {action.title()}!",
            message=f"Your subscription for {product_name} has been {action}.",
            data={"subscription_id": subscription_id}
        )
    
    def create_product_notification(self, user_id: int, product_id: int,
                                   product_name: str) -> Dict:
        """Create new product alert notification"""
        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.PRODUCT.value,
            title="New Product Alert!",
            message=f"Check out our new {product_name} - now available!",
            data={"product_id": product_id}
        )
    
    def get_user_notifications(self, user_id: int) -> List[Dict]:
        """Get all notifications for a user"""
        return [
            n.to_dict() for n in self._notifications.values()
            if n.user_id == user_id
        ]
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications"""
        return sum(
            1 for n in self._notifications.values()
            if n.user_id == user_id and not n.read
        )
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Mark notification as read"""
        if notification_id in self._notifications:
            self._notifications[notification_id].read = True
            return True
        return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user"""
        count = 0
        for n in self._notifications.values():
            if n.user_id == user_id and not n.read:
                n.read = True
                count += 1
        return count
    
    def delete_notification(self, notification_id: int) -> bool:
        """Delete a notification"""
        if notification_id in self._notifications:
            del self._notifications[notification_id]
            return True
        return False


# ==================== GLOBAL INSTANCES ====================

# Create global agent instances for easy access
product_agent = ProductAgent()
cart_agent = CartAgent()
order_agent = OrderAgent()
subscription_agent = SubscriptionAgent()
recommendation_agent = None


def init_recommendation_agent(product_agent: ProductAgent = None) -> RecommendationAgent:
    """Initialize the recommendation agent"""
    global recommendation_agent
    if product_agent is None:
        product_agent = ProductAgent()
    recommendation_agent = RecommendationAgent(product_agent)
    return recommendation_agent


def get_all_agents() -> Dict:
    """Get all agent instances"""
    return {
        "product_agent": product_agent,
        "cart_agent": cart_agent,
        "order_agent": order_agent,
        "subscription_agent": subscription_agent,
        "recommendation_agent": recommendation_agent
    }
