"""
FreshCart AI - E-Commerce Backend
FastAPI application for subscription-based grocery delivery
"""

from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field 
from typing import Optional, List
from api.models import RegisterRequest 
from datetime import datetime, timedelta
import uuid
import hashlib
import pandas as pd
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="FreshCart AI",
    version="1.0.0",
    description="Subscription-based grocery delivery platform"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== DATA STORES ====================

class UserStore:
    """In-memory user storage with authentication"""
    
    def __init__(self):
        self._users = {}
        self._sessions = {}
        self._next_id = 1
        self._create_demo_user()
    
    def _create_demo_user(self):
        """Create demo user for testing"""
        self._users[1] = {
            "id": 1,
            "name": "Demo User",
            "email": "demo@freshcart.ai",
            "phone": "+91 9876543210",
            "address": "123 Demo Street, Mumbai, India",
            "password": self._hash("demo123"),
            "created_at": datetime.now()
        }
        self._next_id = 2
    
    def _hash(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, name: str, email: str, phone: str, address: str, password: str) -> dict:
        """Create a new user"""
        if any(u["email"] == email for u in self._users.values()):
            raise ValueError("Email already registered")
        
        user = {
            "id": self._next_id,
            "name": name,
            "email": email,
            "phone": phone,
            "address": address,
            "password": self._hash(password),
            "created_at": datetime.now()
        }
        self._users[self._next_id] = user
        self._next_id += 1
        return user
    
    def authenticate(self, email: str, password: str) -> Optional[dict]:
        """Authenticate user and return token"""
        for u in self._users.values():
            if u["email"] == email and u["password"] == self._hash(password):
                token = str(uuid.uuid4())
                self._sessions[token] = u["id"]
                return {"user": u, "token": token}
        return None
    
    def get_user(self, token: str) -> Optional[dict]:
        """Get user by token"""
        uid = self._sessions.get(token)
        return self._users.get(uid) if uid else None


class ProductStore:
    """Product catalog storage"""
    
    def __init__(self):
        self._products = self._load_products()
    
    def _load_products(self) -> List[dict]:
        """Load products from CSV or use defaults"""
        path = Path("data/products.csv")
        if path.exists():
            df = pd.read_csv(path)
            return df.to_dict('records')
        return self._default_products()
    
    def _default_products(self) -> List[dict]:
        """Default product catalog"""
        return [
            {"id": 1, "name": "Organic Tomatoes", "category": "vegetables", "price": 3.99, "unit": "kg", "stock": 100, "description": "Farm fresh organic tomatoes", "image_url": "https://images.unsplash.com/photo-1546470427-227c7b3f8311?w=400"},
            {"id": 2, "name": "Fresh Spinach", "category": "vegetables", "price": 2.49, "unit": "bunch", "stock": 80, "description": "Green leafy spinach", "image_url": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400"},
            {"id": 3, "name": "Organic Carrots", "category": "vegetables", "price": 1.99, "unit": "kg", "stock": 120, "description": "Sweet organic carrots", "image_url": "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400"},
            {"id": 4, "name": "Fresh Broccoli", "category": "vegetables", "price": 2.99, "unit": "kg", "stock": 75, "description": "Green broccoli heads", "image_url": "https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=400"},
            {"id": 5, "name": "Crisp Cucumbers", "category": "vegetables", "price": 1.49, "unit": "kg", "stock": 90, "description": "Fresh crunchy cucumbers", "image_url": "https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=400"},
            {"id": 6, "name": "Bell Peppers", "category": "vegetables", "price": 3.49, "unit": "kg", "stock": 60, "description": "Colorful bell peppers", "image_url": "https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400"},
            {"id": 7, "name": "Red Apples", "category": "fruits", "price": 4.99, "unit": "kg", "stock": 200, "description": "Crisp red apples", "image_url": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400"},
            {"id": 8, "name": "Organic Bananas", "category": "fruits", "price": 1.99, "unit": "dozen", "stock": 300, "description": "Ripe organic bananas", "image_url": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=400"},
            {"id": 9, "name": "Fresh Oranges", "category": "fruits", "price": 3.99, "unit": "kg", "stock": 180, "description": "Juicy sweet oranges", "image_url": "https://images.unsplash.com/photo-1547514701-42782101795e?w=400"},
            {"id": 10, "name": "Seedless Grapes", "category": "fruits", "price": 5.99, "unit": "kg", "stock": 120, "description": "Sweet seedless grapes", "image_url": "https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=400"},
            {"id": 11, "name": "Fresh Strawberries", "category": "fruits", "price": 6.99, "unit": "box", "stock": 90, "description": "Organic strawberries", "image_url": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=400"},
            {"id": 12, "name": "Sweet Mangoes", "category": "fruits", "price": 4.49, "unit": "kg", "stock": 100, "description": "Alphonso mangoes", "image_url": "https://images.unsplash.com/photo-1553279768-865429fa0078?w=400"},
            {"id": 13, "name": "Organic Almonds", "category": "nuts", "price": 12.99, "unit": "kg", "stock": 60, "description": "Raw organic almonds", "image_url": "https://images.unsplash.com/photo-1508061253366-f7da158b6d46?w=400"},
            {"id": 14, "name": "Walnuts", "category": "nuts", "price": 14.99, "unit": "kg", "stock": 50, "description": "Fresh shelled walnuts", "image_url": "https://images.unsplash.com/photo-1599593752329-26b651e2efcc?w=400"},
            {"id": 15, "name": "Roasted Cashews", "category": "nuts", "price": 15.99, "unit": "kg", "stock": 45, "description": "Premium roasted cashews", "image_url": "https://images.unsplash.com/photo-1630431341973-02e1b662ec35?w=400"},
            {"id": 16, "name": "Salted Pistachios", "category": "nuts", "price": 13.99, "unit": "kg", "stock": 55, "description": "Roasted pistachios", "image_url": "https://images.unsplash.com/photo-1594942895212-a1b77f48ee92?w=400"},
        ]
    
    def get_all(self) -> List[dict]:
        """Get all products"""
        return self._products
    
    def get_by_id(self, product_id: int) -> Optional[dict]:
        """Get product by ID"""
        return next((p for p in self._products if p["id"] == product_id), None)
    
    def get_by_category(self, category: str) -> List[dict]:
        """Get products by category"""
        return [p for p in self._products if p["category"].lower() == category.lower()]
    
    def search(self, query: str) -> List[dict]:
        """Search products by name or category"""
        query = query.lower()
        return [
            p for p in self._products
            if query in p["name"].lower() or query in p["category"].lower() or query in p["description"].lower()
        ]
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        return list(set(p["category"] for p in self._products))


class OrderStore:
    """Order storage and management"""
    
    def __init__(self):
        self._orders = {}
        self._next_id = 1
    
    def create(
        self,
        user_id: Optional[int],
        items: List[dict],
        subtotal: float,
        delivery_fee: float,
        total: float,
        address: str,
        payment_method: str
    ) -> dict:
        """Create a new order"""
        order = {
            "id": self._next_id,
            "user_id": user_id,
            "items": items,
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "total": total,
            "status": "confirmed",
            "address": address,
            "payment_method": payment_method,
            "created_at": datetime.now().isoformat(),
            "estimated_delivery": (datetime.now() + timedelta(hours=45)).isoformat()
        }
        self._orders[self._next_id] = order
        self._next_id += 1
        return order
    
    def get(self, order_id: int) -> Optional[dict]:
        """Get order by ID"""
        return self._orders.get(order_id)
    
    def get_all(self) -> List[dict]:
        """Get all orders"""
        return list(self._orders.values())
    
    def get_user_orders(self, user_id: int) -> List[dict]:
        """Get orders for a specific user"""
        return [o for o in self._orders.values() if o.get("user_id") == user_id]


class SubscriptionStore:
    """Subscription storage and management"""
    
    def __init__(self):
        self._subscriptions = {}
        self._next_id = 1
    
    def create(
        self,
        user_id: Optional[int],
        product_id: int,
        product_name: str,
        frequency: str,
        quantity: int,
        price: float
    ) -> dict:
        """Create a new subscription"""
        days = {"daily": 1, "weekly": 7, "monthly": 30}.get(frequency, 7)
        subscription = {
            "id": self._next_id,
            "user_id": user_id,
            "product_id": product_id,
            "product_name": product_name,
            "frequency": frequency,
            "quantity": quantity,
            "price": price,
            "total": price * quantity,
            "next_delivery": (datetime.now() + timedelta(days=days)).isoformat(),
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        self._subscriptions[self._next_id] = subscription
        self._next_id += 1
        return subscription
    
    def get_user_subscriptions(self, user_id: int) -> List[dict]:
        """Get active subscriptions for a user"""
        return [s for s in self._subscriptions.values() if s.get("user_id") == user_id and s.get("active")]
    
    def cancel(self, subscription_id: int) -> bool:
        """Cancel a subscription"""
        if subscription_id in self._subscriptions:
            self._subscriptions[subscription_id]["active"] = False
            return True
        return False


class NotificationStore:
    """Notification storage and management"""
    
    def __init__(self):
        self._notifications = {}
        self._next_id = 1
    
    def create(
        self,
        user_id: Optional[int],
        notification_type: str,
        title: str,
        message: str,
        data: Optional[dict] = None
    ) -> dict:
        """Create a new notification"""
        notification = {
            "id": self._next_id,
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "data": data or {},
            "read": False,
            "created_at": datetime.now().isoformat()
        }
        self._notifications[self._next_id] = notification
        self._next_id += 1
        return notification
    
    def get_user_notifications(self, user_id: int) -> List[dict]:
        """Get all notifications for a user"""
        notifications = [n for n in self._notifications.values() if n.get("user_id") == user_id]
        return sorted(notifications, key=lambda x: x["created_at"], reverse=True)
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications"""
        return len([n for n in self._notifications.values() 
                   if n.get("user_id") == user_id and not n.get("read", False)])
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Mark notification as read"""
        if notification_id in self._notifications:
            self._notifications[notification_id]["read"] = True
            return True
        return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user"""
        count = 0
        for n in self._notifications.values():
            if n.get("user_id") == user_id and not n.get("read", False):
                n["read"] = True
                count += 1
        return count
    
    def delete(self, notification_id: int) -> bool:
        """Delete a notification"""
        if notification_id in self._notifications:
            del self._notifications[notification_id]
            return True
        return False
    
    def create_order_notification(self, user_id: int, order_id: int, items: List[dict]) -> dict:
        """Create order confirmation notification"""
        item_names = ", ".join([item.get("name", "Item") for item in items[:2]])
        if len(items) > 2:
            item_names += f" +{len(items) - 2} more"
        return self.create(
            user_id=user_id,
            notification_type="order",
            title="Order Confirmed! 🎉",
            message=f"Your order #{order_id} ({item_names}) has been placed successfully.",
            data={"order_id": order_id, "type": "order"}
        )
    
    def create_delivery_notification(self, user_id: int, order_id: int, status: str) -> dict:
        """Create delivery status notification"""
        status_messages = {
            "preparing": "Your order is being prepared with care!",
            "out_for_delivery": "Your order is on the way! 🚴",
            "delivered": "Your order has been delivered! Enjoy! ✅"
        }
        return self.create(
            user_id=user_id,
            notification_type="delivery",
            title="Delivery Update 📦",
            message=status_messages.get(status, f"Order #{order_id} status: {status}"),
            data={"order_id": order_id, "status": status, "type": "delivery"}
        )
    
    def create_subscription_notification(self, user_id: int, subscription: dict) -> dict:
        """Create subscription renewal notification"""
        return self.create(
            user_id=user_id,
            notification_type="subscription",
            title="Subscription Renewal 🔄",
            message=f"Your {subscription.get('frequency', 'subscription')} subscription for {subscription.get('product_name', 'item')} is renewing soon!",
            data={"subscription_id": subscription.get("id"), "type": "subscription"}
        )
    
    def create_product_notification(self, user_id: int, product: dict) -> dict:
        """Create new product notification"""
        return self.create(
            user_id=user_id,
            notification_type="product",
            title="New Product Alert! 🌟",
            message=f"Check out our new {product.get('name', 'product')} - now available!",
            data={"product_id": product.get("id"), "type": "product"}
        )


# Initialize global stores
users = UserStore()
products = ProductStore()
orders = OrderStore()
subscriptions = SubscriptionStore()
notifications = NotificationStore()


# ==================== PYDANTIC MODELS ====================

class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1)
    password: str 


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1) 
    email: str
    phone: str
    address: str
    password: str = "password123" 


class SubscriptionRequest(BaseModel):
    product_id: int
    frequency: str
    quantity: int = Field(1, ge=1) 


class OrderRequest(BaseModel):
    items: List[dict]
    address: str
    payment_method: str = "cod"


# ==================== AUTH ROUTES ====================

@app.post("/api/auth/register", tags=["Authentication"])
async def register(data: RegisterRequest):
    """Register a new user"""
    try:
        user = users.create_user(
            name=data.name,
            email=data.email,
            phone=data.phone,
            address=data.address,
            password=data.password
        )  
        token = str(uuid.uuid4())
        users._sessions[token] = user["id"]
        return {"user": user, "token": token}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login", tags=["Authentication"])
async def login(data: LoginRequest):
    """Login user and return token"""
    result = users.authenticate(data.email, data.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return result


@app.get("/api/auth/me", tags=["Authentication"])
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current authenticated user"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = users.get_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


# ==================== PRODUCT ROUTES ====================

@app.get("/api/products", tags=["Products"])
async def get_products():
    """Get all products"""
    return products.get_all()


@app.get("/api/products/{product_id}", tags=["Products"])
async def get_product(product_id: int):
    """Get a single product by ID"""
    product = products.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get("/api/products/category/{category}", tags=["Products"]) 
async def get_products_by_category(category: str):
    """Get products by category"""
    return products.get_by_category(category) 

@app.get("/api/products/category/", tags=["Products"])
async def get_products_by_empty_category():
    return products.get_all() 


@app.get("/api/search", tags=["Products"])
async def search_products(q: str = Query(..., description="Search query")):
    """Search products"""
    return products.search(q)


@app.get("/api/categories", tags=["Products"])
async def get_categories():
    """Get all product categories"""
    return products.get_categories()


# ==================== CART ROUTES ====================

@app.post("/api/cart/add", tags=["Cart"])
async def add_to_cart(
    product_id: int,
    quantity: int = Query(1, ge=0)
): 
    """Add item to cart (mock - returns product info)"""
    product = products.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Added to cart", "product": product, "quantity": quantity}


# ==================== SUBSCRIPTION ROUTES ====================

@app.post("/api/subscriptions", tags=["Subscriptions"])
async def create_subscription(
    data: SubscriptionRequest,
    authorization: Optional[str] = Header(None)
):
    """Create a new subscription"""
    product = products.get_by_id(data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    user_id = None
    if authorization:
        token = authorization.replace("Bearer ", "")
        user = users.get_user(token)
        if user:
            user_id = user["id"]
    
    return subscriptions.create(
        user_id=user_id,
        product_id=data.product_id,
        product_name=product["name"],
        frequency=data.frequency,
        quantity=data.quantity,
        price=product["price"]
    )


@app.get("/api/subscriptions", tags=["Subscriptions"])
async def get_subscriptions(authorization: Optional[str] = Header(None)):
    """Get user's subscriptions"""
    if authorization:
        token = authorization.replace("Bearer ", "")
        user = users.get_user(token)
        if user:
            return subscriptions.get_user_subscriptions(user["id"])
    return []


@app.delete("/api/subscriptions/{subscription_id}", tags=["Subscriptions"])
async def cancel_subscription(subscription_id: int):
    """Cancel a subscription"""
    if not subscriptions.cancel(subscription_id):
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"message": "Subscription cancelled"}


@app.get("/api/subscription-plans", tags=["Subscriptions"])
async def get_subscription_plans():
    """Get available subscription plans"""
    return [
        {
            "id": "daily",
            "name": "Daily Fresh",
            "description": "Get fresh delivery every day",
            "icon": "📅",
            "price": 9,
            "benefits": ["Daily delivery", "Always fresh", "Flexible skip days"]
        },
        {
            "id": "weekly",
            "name": "Weekly Bundle",
            "description": "Weekly delivery with savings",
            "icon": "📦",
            "price": 19,
            "benefits": ["Weekly delivery", "10% off", "Free delivery", "Skip anytime"]
        },
        {
            "id": "monthly",
            "name": "Monthly Mega",
            "description": "Monthly subscription with best savings",
            "icon": "🎁",
            "price": 29,
            "benefits": ["Monthly delivery", "20% off", "Priority support", "Free delivery", "Exclusive deals"]
        }
    ]


# ==================== ORDER ROUTES ====================

@app.post("/api/orders", tags=["Orders"])
async def place_order(
    data: OrderRequest,
    authorization: Optional[str] = Header(None)
):
    """Place a new order"""
    if not data.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    user_id = None
    address = data.address
    
    if authorization:
        token = authorization.replace("Bearer ", "")
        user = users.get_user(token)
        if user:
            user_id = user["id"]
            address = user.get("address", data.address)
    
    subtotal = sum(item["price"] * item["quantity"] for item in data.items)
    delivery_fee = 2.99
    total = subtotal + delivery_fee
    
    items = [
        {
            "product_id": item["product_id"],
            "name": item["name"],
            "price": item["price"],
            "quantity": item["quantity"],
            "subtotal": item["price"] * item["quantity"]
        }
        for item in data.items
    ]
    
    order = orders.create(
        user_id=user_id,
        items=items,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
        address=address,
        payment_method=data.payment_method
    )
    
    if user_id:
        notifications.create_order_notification(user_id, order["id"], items)
    
    return order


@app.get("/api/orders", tags=["Orders"])
async def get_orders(authorization: Optional[str] = Header(None)):
    """Get user's orders"""
    if authorization:
        token = authorization.replace("Bearer ", "")
        user = users.get_user(token)
        if user:
            return orders.get_user_orders(user["id"])
    return orders.get_all()


@app.get("/api/orders/{order_id}", tags=["Orders"])
async def get_order(order_id: int):
    """Get order details"""
    order = orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.get("/api/orders/track/{order_id}", tags=["Orders"])
async def track_order(order_id: int):
    """Track order status"""
    order = orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    status_flow = ["confirmed", "preparing", "out_for_delivery", "delivered"]
    current_index = status_flow.index(order["status"]) if order["status"] in status_flow else 0
    
    timeline = [
        {
            "status": "Order Confirmed",
            "time": order["created_at"],
            "completed": True
        },
        {
            "status": "Preparing",
            "time": None,
            "completed": current_index >= 1
        },
        {
            "status": "Out for Delivery",
            "time": None,
            "completed": current_index >= 2
        },
        {
            "status": "Delivered",
            "time": order.get("estimated_delivery") if current_index >= 3 else None,
            "completed": current_index >= 3
        }
    ]
    
    return {
        "order_id": order["id"],
        "status": order["status"],
        "estimated_delivery": order.get("estimated_delivery"),
        "timeline": timeline
    }


# ==================== HEALTH CHECK ====================

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FreshCart AI API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# ==================== NOTIFICATION ROUTES ====================

@app.get("/api/notifications", tags=["Notifications"])
async def get_notifications(authorization: Optional[str] = Header(None)):
    """Get user's notifications"""
    if authorization:
        token = authorization.replace("Bearer ", "")
        user = users.get_user(token)
        if user:
            return notifications.get_user_notifications(user["id"])
    return []


@app.get("/api/notifications/unread-count", tags=["Notifications"])
async def get_unread_count(authorization: Optional[str] = Header(None)):
    """Get count of unread notifications"""
    if authorization:
        token = authorization.replace("Bearer ", "")
        user = users.get_user(token)
        if user:
            return {"count": notifications.get_unread_count(user["id"])}
    return {"count": 0}


@app.post("/api/notifications/{notification_id}/read", tags=["Notifications"])
async def mark_notification_read(notification_id: int, authorization: Optional[str] = Header(None)):
    """Mark a notification as read"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = users.get_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    success = notifications.mark_as_read(notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}


@app.post("/api/notifications/read-all", tags=["Notifications"])
async def mark_all_notifications_read(authorization: Optional[str] = Header(None)):
    """Mark all notifications as read"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = users.get_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    count = notifications.mark_all_as_read(user["id"])
    return {"message": f"Marked {count} notifications as read"}


@app.delete("/api/notifications/{notification_id}", tags=["Notifications"])
async def delete_notification(notification_id: int, authorization: Optional[str] = Header(None)):
    """Delete a notification"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    user = users.get_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    success = notifications.delete(notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted"}


# ==================== HEALTH CHECK ====================

@app.get("/api/health", tags=["Info"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "products": len(products.get_all()),
        "orders": len(orders.get_all()),
        "subscriptions": len(subscriptions._subscriptions)
    }


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
