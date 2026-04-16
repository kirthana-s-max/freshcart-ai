# FreshCart AI - Multi-Agent System

## Agent Definitions

This document defines all agents using structured markdown format. Each agent is defined with YAML frontmatter and executable code blocks.

---

## ProductAgent

```yaml
name: ProductAgent
version: 1.0.0
description: Manages product catalog with data loaded from data/products.csv
storage: csv
data_source: data/products.csv
```

### Capabilities

- Load and cache products from CSV
- Search by name, category, or description
- Filter by category (vegetables, fruits, nuts)
- Get low stock alerts

### Methods

#### get_all_products()
```python
def get_all_products() -> List[dict]:
    """Get all products from catalog"""
    df = self._load_products()
    return df.to_dict('records')
```

#### get_products_by_category(category: str)
```python
def get_products_by_category(self, category: str) -> List[dict]:
    """Filter products by category"""
    df = self._load_products()
    filtered = df[df['category'].str.lower() == category.lower()]
    return filtered.to_dict('records')
```

#### search_products(keyword: str)
```python
def search_products(self, keyword: str) -> List[dict]:
    """Search by name, category, or description"""
    df = self._load_products()
    keyword_lower = keyword.lower()
    filtered = df[
        df['name'].str.lower().str.contains(keyword_lower, na=False) |
        df['category'].str.lower().str.contains(keyword_lower, na=False) |
        df['description'].str.lower().str.contains(keyword_lower, na=False)
    ]
    return filtered.to_dict('records')
```

#### get_product_by_id(product_id: int)
```python
def get_product_by_id(self, product_id: int) -> Optional[dict]:
    """Get single product by ID"""
    df = self._load_products()
    product = df[df['id'] == product_id]
    if product.empty:
        return None
    return product.iloc[0].to_dict()
```

#### get_categories()
```python
def get_categories(self) -> List[str]:
    """Get all available categories"""
    df = self._load_products()
    return df['category'].unique().tolist()
```

---

## CartAgent

```yaml
name: CartAgent
version: 1.0.0
description: Handles shopping cart operations with in-memory storage
storage: memory
delivery_fee: 2.99
```

### Capabilities

- Add/remove items from cart
- Update quantities
- Calculate totals with delivery fee
- Persist cart to localStorage (frontend)

### Methods

#### add_item(product_id, name, price, quantity, unit)
```python
def add_item(self, product_id: int, name: str, price: float, quantity: int = 1, unit: str = "") -> Dict:
    """Add item to cart or increase quantity"""
    if product_id in self._cart:
        self._cart[product_id].quantity += quantity
    else:
        self._cart[product_id] = CartItem(product_id, name, price, quantity, unit)
    return self._cart[product_id].to_dict()
```

#### remove_item(product_id: int)
```python
def remove_item(self, product_id: int) -> bool:
    """Remove item from cart"""
    if product_id in self._cart:
        del self._cart[product_id]
        return True
    return False
```

#### view_cart()
```python
def view_cart(self) -> List[Dict]:
    """Get all cart items"""
    return [item.to_dict() for item in self._cart.values()]
```

#### calculate_total()
```python
def calculate_total(self) -> Dict:
    """Calculate subtotal, fees, total"""
    items = self.view_cart()
    subtotal = sum(item['subtotal'] for item in items)
    delivery_fee = self.DELIVERY_FEE if items else 0
    total = subtotal + delivery_fee
    return {
        "items": items,
        "subtotal": round(subtotal, 2),
        "delivery_fee": delivery_fee,
        "total": round(total, 2)
    }
```

---

## OrderAgent

```yaml
name: OrderAgent
version: 1.0.0
description: Processes customer orders with status tracking
storage: memory
statuses: [pending, confirmed, preparing, shipped, delivered, cancelled]
```

### Capabilities

- Create new orders
- Track order status
- Cancel orders
- Get order history

### Methods

#### place_order(items, total, address)
```python
def place_order(self, items: List[Dict], total: float, address: str = "") -> Dict:
    """Create new order"""
    order = Order(order_id=self._next_id, items=items, total=total, address=address)
    self._orders[self._next_id] = order
    self._next_id += 1
    return order.to_dict()
```

#### get_order_history()
```python
def get_order_history(self) -> List[Dict]:
    """Get all orders"""
    return [order.to_dict() for order in self._orders.values()]
```

#### get_order_by_id(order_id: int)
```python
def get_order_by_id(self, order_id: int) -> Optional[Dict]:
    """Get specific order"""
    if order_id in self._orders:
        return self._orders[order_id].to_dict()
    return None
```

#### cancel_order(order_id: int)
```python
def cancel_order(self, order_id: int) -> bool:
    """Cancel an order"""
    if order_id in self._orders:
        self._orders[order_id].status = "cancelled"
        return True
    return False
```

---

## SubscriptionAgent

```yaml
name: SubscriptionAgent
version: 1.0.0
description: Manages recurring product subscriptions
storage: memory
frequencies: [daily, weekly, monthly]
```

### Capabilities

- Create subscriptions with configurable frequency
- Track next delivery dates
- Cancel/reactivate subscriptions

### Methods

#### create_subscription(product_id, product_name, frequency, quantity, price)
```python
def create_subscription(self, product_id: int, product_name: str,
                       frequency: str, quantity: int, price: float) -> Dict:
    """Create subscription"""
    valid_frequencies = ["daily", "weekly", "monthly"]
    if frequency.lower() not in valid_frequencies:
        raise ValueError(f"Invalid frequency")
    
    days = {"daily": 1, "weekly": 7, "monthly": 30}[frequency.lower()]
    subscription = {
        "id": self._next_id,
        "product_id": product_id,
        "product_name": product_name,
        "frequency": frequency.lower(),
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
```

#### get_active_subscriptions()
```python
def get_active_subscriptions(self) -> List[Dict]:
    """Get all active subscriptions"""
    return [s for s in self._subscriptions.values() if s["active"]]
```

#### cancel_subscription(subscription_id: int)
```python
def cancel_subscription(self, subscription_id: int) -> bool:
    """Cancel subscription"""
    if subscription_id in self._subscriptions:
        self._subscriptions[subscription_id]["active"] = False
        return True
    return False
```

---

## NotificationAgent

```yaml
name: NotificationAgent
version: 1.0.0
description: Manages user notifications
storage: memory
types: [order, delivery, subscription, product, promo]
```

### Capabilities

- Create notifications for orders, deliveries, subscriptions, products
- Track read/unread status
- Mark as read, delete notifications

### Methods

#### create_notification(user_id, type, title, message, data)
```python
def create_notification(self, user_id: int, notification_type: str,
                        title: str, message: str, data: dict = None) -> Dict:
    """Create new notification"""
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
```

#### create_order_notification(user_id, order_id, items)
```python
def create_order_notification(self, user_id: int, order_id: int, items: List[Dict]) -> Dict:
    """Create order confirmation notification"""
    item_names = [item.get('name', 'Item') for item in items[:3]]
    items_text = ", ".join(item_names)
    if len(items) > 3:
        items_text += f" and {len(items) - 3} more"
    
    return self.create_notification(
        user_id=user_id,
        notification_type="order",
        title="Order Confirmed!",
        message=f"Your order #{order_id} ({items_text}) has been placed.",
        data={"order_id": order_id}
    )
```

#### get_user_notifications(user_id: int)
```python
def get_user_notifications(self, user_id: int) -> List[Dict]:
    """Get all notifications for user"""
    return [n for n in self._notifications.values() if n["user_id"] == user_id]
```

#### mark_as_read(notification_id: int)
```python
def mark_as_read(self, notification_id: int) -> bool:
    """Mark notification as read"""
    if notification_id in self._notifications:
        self._notifications[notification_id]["read"] = True
        return True
    return False
```

---

## RecommendationAgent

```yaml
name: RecommendationAgent
version: 1.0.0
description: Provides personalized product recommendations
storage: none
dependencies: [ProductAgent]
```

### Capabilities

- Recommend similar products
- Get popular products
- Suggest complementary items
- Create meal bundle suggestions

### Methods

#### recommend_by_product(product_id: int)
```python
def recommend_by_product(self, product_id: int) -> List[Dict]:
    """Get similar products"""
    product = self.product_agent.get_product_by_id(product_id)
    if not product:
        return []
    return self.recommend_by_category(product['category'])
```

#### recommend_by_category(category: str, limit: int = 5)
```python
def recommend_by_category(self, category: str, limit: int = 5) -> List[Dict]:
    """Get products from same category"""
    products = self.product_agent.get_products_by_category(category)
    return random.sample(products, min(limit, len(products))) if len(products) > limit else products
```

#### get_complementary_products(product_id: int)
```python
def get_complementary_products(self, product_id: int) -> List[Dict]:
    """Get products from related categories"""
    product = self.product_agent.get_product_by_id(product_id)
    if not product:
        return []
    
    complementary = {'vegetables': 'fruits', 'fruits': 'nuts', 'nuts': 'vegetables'}
    related = complementary.get(product['category'], 'vegetables')
    return self.recommend_by_category(related, limit=3)
```

---

## Orchestration

```yaml
orchestrator:
  name: FreshCartOrchestrator
  version: 1.0.0
  agents:
    - ProductAgent
    - CartAgent
    - OrderAgent
    - SubscriptionAgent
    - NotificationAgent
    - RecommendationAgent
  workflow:
    - name: order_placement
      agents: [CartAgent, OrderAgent, NotificationAgent]
      description: Handle order from cart to confirmation
    - name: product_discovery
      agents: [ProductAgent, RecommendationAgent]
      description: Search and recommend products
    - name: subscription_management
      agents: [SubscriptionAgent, NotificationAgent]
      description: Manage recurring deliveries
```

### Workflow: order_placement

1. **CartAgent** → Validates cart items
2. **OrderAgent** → Creates order with status
3. **NotificationAgent** → Sends order confirmation

### Workflow: product_discovery

1. **ProductAgent** → Searches/filters products
2. **RecommendationAgent** → Suggests similar/complementary items

### Workflow: subscription_management

1. **SubscriptionAgent** → Creates/manages subscription
2. **NotificationAgent** → Sends renewal reminders
