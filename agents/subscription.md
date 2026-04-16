# SubscriptionAgent

```yaml
name: SubscriptionAgent
version: 1.0.0
description: Manages recurring product subscriptions with configurable frequencies
storage: memory
frequencies:
  - daily
  - weekly
  - monthly
delivery_days:
  daily: 1
  weekly: 7
  monthly: 30
```

## Overview

SubscriptionAgent handles recurring product subscriptions, allowing customers to set up automatic deliveries at configurable intervals. It manages the subscription lifecycle including creation, tracking, cancellation, and reactivation.

## Capabilities

- Create subscriptions with daily/weekly/monthly frequency
- Track next delivery dates automatically
- Cancel subscriptions
- Reactivate cancelled subscriptions
- Get active subscriptions
- Get subscriptions by user
- Get subscription by ID

## Subscription Frequencies

| Frequency | Delivery Interval | Days |
|-----------|------------------|------|
| daily | Every day | 1 |
| weekly | Every week | 7 |
| monthly | Every month | 30 |

## Methods

### create_subscription(product_id, product_name, frequency, quantity, price, user_id=None)

Creates a new recurring subscription.

```python
def create_subscription(self, product_id: int, product_name: str,
                       frequency: str, quantity: int, price: float,
                       user_id: int = None) -> Dict:
    valid_freqs = ["daily", "weekly", "monthly"]
    if frequency.lower() not in valid_freqs:
        raise ValueError(f"Invalid frequency. Must be one of: {valid_freqs}")
    
    days = {"daily": 1, "weekly": 7, "monthly": 30}[frequency.lower()]
    subscription = {
        "id": self._next_id,
        "user_id": user_id,
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

**Parameters:**
- `product_id` (int) - Product identifier
- `product_name` (str) - Product name
- `frequency` (str) - Delivery frequency (daily, weekly, monthly)
- `quantity` (int) - Quantity per delivery
- `price` (float) - Price per unit
- `user_id` (int, optional) - User identifier

**Returns:** Created subscription dict

**Raises:** ValueError if frequency is invalid

---

### get_active_subscriptions()

Gets all active subscriptions.

```python
def get_active_subscriptions(self) -> List[Dict]:
    return [s for s in self._subscriptions.values() if s["active"]]
```

**Returns:** List of active subscriptions

---

### get_user_subscriptions(user_id: int)

Gets all active subscriptions for a user.

```python
def get_user_subscriptions(self, user_id: int) -> List[Dict]:
    return [s for s in self._subscriptions.values() 
            if s.get("user_id") == user_id and s["active"]]
```

**Parameters:**
- `user_id` (int) - User identifier

**Returns:** List of user's active subscriptions

---

### get_all_subscriptions()

Gets all subscriptions (active and inactive).

```python
def get_all_subscriptions(self) -> List[Dict]:
    return list(self._subscriptions.values())
```

**Returns:** List of all subscriptions

---

### cancel_subscription(subscription_id: int)

Cancels a subscription.

```python
def cancel_subscription(self, subscription_id: int) -> bool:
    if subscription_id in self._subscriptions:
        self._subscriptions[subscription_id]["active"] = False
        return True
    return False
```

**Parameters:**
- `subscription_id` (int) - Subscription identifier

**Returns:** True if cancelled, False if not found

---

### reactivate_subscription(subscription_id: int)

Reactives a cancelled subscription.

```python
def reactivate_subscription(self, subscription_id: int) -> bool:
    if subscription_id in self._subscriptions:
        self._subscriptions[subscription_id]["active"] = True
        return True
    return False
```

**Parameters:**
- `subscription_id` (int) - Subscription identifier

**Returns:** True if reactivated, False if not found

---

### get_subscription_by_id(subscription_id: int)

Gets a subscription by ID.

```python
def get_subscription_by_id(self, subscription_id: int) -> Optional[Dict]:
    if subscription_id in self._subscriptions:
        return self._subscriptions[subscription_id]
    return None
```

**Parameters:**
- `subscription_id` (int) - Subscription identifier

**Returns:** Subscription dict or None

---

### update_next_delivery(subscription_id: int)

Updates the next delivery date based on frequency.

```python
def update_next_delivery(self, subscription_id: int) -> bool:
    if subscription_id not in self._subscriptions:
        return False
    
    sub = self._subscriptions[subscription_id]
    days = {"daily": 1, "weekly": 7, "monthly": 30}[sub["frequency"]]
    sub["next_delivery"] = (datetime.now() + timedelta(days=days)).isoformat()
    return True
```

**Parameters:**
- `subscription_id` (int) - Subscription identifier

**Returns:** True if updated, False if not found

---

## Data Schema

| Field | Type | Description |
|-------|------|-------------|
| id | int | Unique subscription identifier |
| user_id | int | User identifier |
| product_id | int | Product identifier |
| product_name | str | Product name |
| frequency | str | Delivery frequency |
| quantity | int | Quantity per delivery |
| price | float | Price per unit |
| total | float | Total per delivery (price × quantity) |
| next_delivery | datetime | Next delivery date |
| active | bool | Subscription status |
| created_at | datetime | Creation timestamp |

## Usage Example

```python
from agents import get_subscription_agent

subscriptions = get_subscription_agent()

# Create subscription
sub = subscriptions.create_subscription(
    product_id=1,
    product_name="Organic Tomatoes",
    frequency="weekly",
    quantity=2,
    price=7.98,
    user_id=1
)
print(f"Subscription #{sub['id']} created")
print(f"Next delivery: {sub['next_delivery']}")

# Get user's subscriptions
my_subs = subscriptions.get_user_subscriptions(1)

# Get all active subscriptions
active = subscriptions.get_active_subscriptions()

# Cancel subscription
subscriptions.cancel_subscription(1)

# Reactivate subscription
subscriptions.reactivate_subscription(1)

# Get subscription details
sub_details = subscriptions.get_subscription_by_id(1)
```

## Workflow Integration

SubscriptionAgent is used in the `subscription_management` workflow:

1. SubscriptionAgent creates/updates subscriptions
2. NotificationAgent sends renewal reminders

## Events

| Event | Trigger | Action |
|-------|---------|--------|
| subscription_created | create_subscription() | Set active=True |
| subscription_cancelled | cancel_subscription() | Set active=False |
| subscription_reactivated | reactivate_subscription() | Set active=True |
| delivery_completed | update_next_delivery() | Update next_delivery |

## Price Calculation

```
total = price × quantity

Examples:
- Tomatoes: $3.99/kg × 2kg = $7.98
- Apples: $4.99/kg × 5kg = $24.95
```
