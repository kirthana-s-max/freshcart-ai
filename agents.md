# FreshCart AI - Agents Documentation

This document describes all AI agents used in the FreshCart e-commerce platform.

## Overview

FreshCart AI uses a multi-agent architecture where each agent is responsible for a specific domain of functionality:

| Agent | File | Purpose |
|-------|------|---------|
| ProductAgent | `product_agent.py` | Product catalog management |
| CartAgent | `cart_agent.py` | Shopping cart operations |
| OrderAgent | `order_agent.py` | Order processing |
| SubscriptionAgent | `subscription_agent.py` | Subscription management |
| RecommendationAgent | `recommendation_agent.py` | Product recommendations |
| NotificationAgent | `notification_agent.py` | User notifications |

---

## ProductAgent

Manages the product catalog with data loaded from `data/products.csv`.

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `get_all_products()` | Get all products from catalog | `List[dict]` |
| `get_products_by_category(category)` | Filter products by category | `List[dict]` |
| `search_products(keyword)` | Search by name, category, or description | `List[dict]` |
| `get_product_by_id(product_id)` | Get single product by ID | `Optional[dict]` |
| `get_categories()` | Get all available categories | `List[str]` |
| `get_low_stock_products(threshold)` | Get products with low stock | `List[dict]` |

### Example

```python
from agents.product_agent import ProductAgent

agent = ProductAgent()
products = agent.get_all_products()
vegetables = agent.get_products_by_category("vegetables")
results = agent.search_products("organic")
```

---

## CartAgent

Handles shopping cart operations with in-memory storage.

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `add_item(product_id, name, price, quantity, unit)` | Add or update cart item | `Dict` |
| `remove_item(product_id)` | Remove item from cart | `bool` |
| `update_quantity(product_id, quantity)` | Update item quantity | `Optional[Dict]` |
| `view_cart()` | Get all cart items | `List[Dict]` |
| `calculate_total()` | Calculate subtotal, fees, total | `Dict` |
| `clear_cart()` | Empty the cart | `None` |
| `get_cart_count()` | Total items in cart | `int` |
| `is_empty()` | Check if cart is empty | `bool` |

### Example

```python
from agents.cart_agent import CartAgent

cart = CartAgent()
cart.add_item(1, "Organic Tomatoes", 3.99, 2, "kg")
cart.add_item(7, "Red Apples", 4.99, 1, "kg")
total = cart.calculate_total()
# {'items': [...], 'subtotal': 11.97, 'delivery_fee': 2.99, 'total': 14.96}
```

---

## OrderAgent

Processes customer orders with status tracking.

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `place_order(items, total, address)` | Create new order | `Dict` |
| `get_order_history()` | Get all orders | `List[Dict]` |
| `get_user_orders(user_id)` | Get orders for user | `List[Dict]` |
| `get_order_by_id(order_id)` | Get specific order | `Optional[Dict]` |
| `update_status(order_id, status)` | Update order status | `bool` |
| `cancel_order(order_id)` | Cancel an order | `bool` |

### Order Statuses

- `pending` - Order placed, awaiting confirmation
- `confirmed` - Order confirmed
- `preparing` - Order being prepared
- `shipped` - Order shipped
- `delivered` - Order delivered
- `cancelled` - Order cancelled

### Example

```python
from agents.order_agent import OrderAgent

orders = OrderAgent()
order = orders.place_order(
    items=[{"product_id": 1, "name": "Tomatoes", "price": 3.99, "quantity": 2}],
    total=11.97,
    address="123 Main St"
)
```

---

## SubscriptionAgent

Manages recurring product subscriptions with configurable frequencies.

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `create_subscription(product_id, name, frequency, quantity, price)` | Create subscription | `Dict` |
| `get_active_subscriptions()` | Get all active subscriptions | `List[Dict]` |
| `get_user_subscriptions(user_id)` | Get user's subscriptions | `List[Dict]` |
| `get_all_subscriptions()` | Get all subscriptions | `List[Dict]` |
| `cancel_subscription(subscription_id)` | Cancel subscription | `bool` |
| `reactivate_subscription(subscription_id)` | Reactivate subscription | `bool` |
| `get_subscription_by_id(subscription_id)` | Get subscription details | `Optional[Dict]` |

### Subscription Frequencies

- `daily` - Delivered every day
- `weekly` - Delivered every 7 days
- `monthly` - Delivered every 30 days

### Example

```python
from agents.subscription_agent import SubscriptionAgent

subs = SubscriptionAgent()
sub = subs.create_subscription(
    product_id=1,
    product_name="Organic Tomatoes",
    frequency="weekly",
    quantity=2,
    price=7.98
)
```

---

## RecommendationAgent

Provides personalized product recommendations using category-based filtering.

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `recommend_by_product(product_id)` | Similar products | `List[Dict]` |
| `recommend_by_category(category, limit)` | Products in category | `List[Dict]` |
| `get_popular_products(limit)` | Popular products | `List[Dict]` |
| `get_complementary_products(product_id)` | Related category products | `List[Dict]` |
| `get_bundle_suggestions(cart_items)` | Complete meal bundles | `List[Dict]` |

### Complementary Categories

| Category | Complements |
|----------|-------------|
| vegetables | fruits |
| fruits | nuts |
| nuts | vegetables |

### Example

```python
from agents.recommendation_agent import RecommendationAgent

rec = RecommendationAgent(product_agent)
similar = rec.recommend_by_product(1)
popular = rec.get_popular_products(5)
bundles = rec.get_bundle_suggestions(cart_items)
```

---

## NotificationAgent

Manages user notifications for orders, deliveries, subscriptions, and products.

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `create_notification(user_id, type, title, message, data)` | Create notification | `Dict` |
| `create_order_notification(user_id, order_id, items)` | Order confirmation | `Dict` |
| `create_delivery_notification(user_id, order_id, status, message)` | Delivery update | `Dict` |
| `create_subscription_notification(user_id, sub_id, product, action)` | Subscription update | `Dict` |
| `create_product_notification(user_id, product_id, name)` | New product alert | `Dict` |
| `get_user_notifications(user_id)` | Get user notifications | `List[Dict]` |
| `get_unread_count(user_id)` | Count unread notifications | `int` |
| `mark_as_read(notification_id)` | Mark as read | `bool` |
| `mark_all_as_read(user_id)` | Mark all as read | `int` |
| `delete_notification(notification_id)` | Delete notification | `bool` |

### Notification Types

- `order` - Order confirmations
- `delivery` - Delivery status updates
- `subscription` - Subscription renewals/cancellations
- `product` - New product alerts
- `promo` - Promotional notifications

### Example

```python
from agents.notification_agent import NotificationAgent

notifs = NotificationAgent()
notifs.create_order_notification(1, 101, [{"name": "Tomatoes", "quantity": 2}])
count = notifs.get_unread_count(1)
notifs.mark_all_as_read(1)
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      FreshCart AI                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Product   │    │    Cart     │    │   Order     │     │
│  │   Agent     │    │   Agent     │    │   Agent     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                 │                  │              │
│         └────────┬────────┴────────┬─────────┘              │
│                  │                │                        │
│         ┌────────▼──────┐  ┌───────▼────────┐              │
│         │Recommendation│  │ Notification  │              │
│         │    Agent     │  │    Agent      │              │
│         └──────────────┘  └───────────────┘              │
│                                                             │
│  ┌─────────────────────────────────────────────────┐       │
│  │              SubscriptionAgent                   │       │
│  └─────────────────────────────────────────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Usage with FastAPI Backend

The agents are integrated with the main FastAPI application in `main.py`:

```python
from main import products, cart, orders, subscriptions, notifications

# Get products
all_products = products.get_all()

# Create order
order = orders.create(user_id=1, items=[...], total=25.99, ...)

# Create subscription
sub = subscriptions.create(user_id=1, product_id=1, ...)
```
