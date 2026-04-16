# NotificationAgent

```yaml
name: NotificationAgent
version: 1.0.0
description: Manages user notifications for orders, deliveries, subscriptions, and products
storage: memory
types:
  - order
  - delivery
  - subscription
  - product
  - promo
auto_create:
  order_confirmation: true
  delivery_update: false
  subscription_reminder: false
  product_alert: false
```

## Overview

NotificationAgent handles all notification-related operations, creating and managing notifications for various user events including order confirmations, delivery updates, subscription reminders, and new product alerts.

## Capabilities

- Create general notifications
- Create order confirmation notifications
- Create delivery status notifications
- Create subscription notifications
- Create product alert notifications
- Get user notifications
- Get unread notification count
- Mark notifications as read
- Mark all notifications as read
- Delete notifications

## Notification Types

| Type | Icon | Description |
|------|------|-------------|
| order | 📦 | Order confirmations and updates |
| delivery | 🚚 | Delivery status updates |
| subscription | 🔄 | Subscription renewals/cancellations |
| product | ✨ | New product alerts |
| promo | 🎉 | Promotional notifications |

## Methods

### create_notification(user_id, type, title, message, data=None)

Creates a new notification.

```python
def create_notification(self, user_id: int, notification_type: str,
                        title: str, message: str, data: dict = None) -> Dict:
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

**Parameters:**
- `user_id` (int) - User identifier
- `type` (str) - Notification type
- `title` (str) - Notification title
- `message` (str) - Notification message
- `data` (dict, optional) - Additional data

**Returns:** Created notification dict

---

### create_order_notification(user_id, order_id, items)

Creates an order confirmation notification.

```python
def create_order_notification(self, user_id: int, order_id: int, 
                              items: List[Dict]) -> Dict:
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

**Parameters:**
- `user_id` (int) - User identifier
- `order_id` (int) - Order identifier
- `items` (List[Dict]) - Order items

**Returns:** Created notification dict

---

### create_delivery_notification(user_id, order_id, status, message)

Creates a delivery status notification.

```python
def create_delivery_notification(self, user_id: int, order_id: int,
                                 status: str, message: str) -> Dict:
    return self.create_notification(
        user_id=user_id,
        notification_type="delivery",
        title=f"Delivery Update - Order #{order_id}",
        message=message,
        data={"order_id": order_id, "status": status}
    )
```

**Parameters:**
- `user_id` (int) - User identifier
- `order_id` (int) - Order identifier
- `status` (str) - Delivery status
- `message` (str) - Status message

**Returns:** Created notification dict

---

### create_subscription_notification(user_id, subscription_id, product_name, action)

Creates a subscription notification.

```python
def create_subscription_notification(self, user_id: int, subscription_id: int,
                                     product_name: str, action: str) -> Dict:
    return self.create_notification(
        user_id=user_id,
        notification_type="subscription",
        title=f"Subscription {action.title()}!",
        message=f"Your subscription for {product_name} has been {action}.",
        data={"subscription_id": subscription_id}
    )
```

**Parameters:**
- `user_id` (int) - User identifier
- `subscription_id` (int) - Subscription identifier
- `product_name` (str) - Product name
- `action` (str) - Action (created, renewed, cancelled)

**Returns:** Created notification dict

---

### create_product_notification(user_id, product_id, product_name)

Creates a new product alert notification.

```python
def create_product_notification(self, user_id: int, product_id: int,
                               product_name: str) -> Dict:
    return self.create_notification(
        user_id=user_id,
        notification_type="product",
        title="New Product Alert!",
        message=f"Check out our new {product_name} - now available!",
        data={"product_id": product_id}
    )
```

**Parameters:**
- `user_id` (int) - User identifier
- `product_id` (int) - Product identifier
- `product_name` (str) - Product name

**Returns:** Created notification dict

---

### get_user_notifications(user_id: int)

Gets all notifications for a user.

```python
def get_user_notifications(self, user_id: int) -> List[Dict]:
    return [n for n in self._notifications.values() 
            if n["user_id"] == user_id]
```

**Parameters:**
- `user_id` (int) - User identifier

**Returns:** List of user's notifications

---

### get_unread_count(user_id: int)

Gets count of unread notifications.

```python
def get_unread_count(self, user_id: int) -> int:
    return sum(1 for n in self._notifications.values() 
               if n["user_id"] == user_id and not n["read"])
```

**Parameters:**
- `user_id` (int) - User identifier

**Returns:** Count of unread notifications

---

### mark_as_read(notification_id: int)

Marks a notification as read.

```python
def mark_as_read(self, notification_id: int) -> bool:
    if notification_id in self._notifications:
        self._notifications[notification_id]["read"] = True
        return True
    return False
```

**Parameters:**
- `notification_id` (int) - Notification identifier

**Returns:** True if marked, False if not found

---

### mark_all_as_read(user_id: int)

Marks all notifications as read for a user.

```python
def mark_all_as_read(self, user_id: int) -> int:
    count = 0
    for n in self._notifications.values():
        if n["user_id"] == user_id and not n["read"]:
            n["read"] = True
            count += 1
    return count
```

**Parameters:**
- `user_id` (int) - User identifier

**Returns:** Number of notifications marked as read

---

### delete_notification(notification_id: int)

Deletes a notification.

```python
def delete_notification(self, notification_id: int) -> bool:
    if notification_id in self._notifications:
        del self._notifications[notification_id]
        return True
    return False
```

**Parameters:**
- `notification_id` (int) - Notification identifier

**Returns:** True if deleted, False if not found

---

## Data Schema

| Field | Type | Description |
|-------|------|-------------|
| id | int | Unique notification identifier |
| user_id | int | User identifier |
| type | str | Notification type |
| title | str | Notification title |
| message | str | Notification message |
| data | dict | Additional data |
| read | bool | Read status |
| created_at | datetime | Creation timestamp |

## Usage Example

```python
from agents import get_notification_agent

notifications = get_notification_agent()

# Create order notification
notif = notifications.create_order_notification(
    user_id=1,
    order_id=101,
    items=[
        {"name": "Tomatoes", "quantity": 2},
        {"name": "Apples", "quantity": 3}
    ]
)
print(f"Notification: {notif['title']}")

# Get user notifications
my_notifs = notifications.get_user_notifications(1)

# Get unread count
unread = notifications.get_unread_count(1)
print(f"Unread: {unread}")

# Mark as read
notifications.mark_as_read(1)

# Mark all as read
notifications.mark_all_as_read(1)

# Delete notification
notifications.delete_notification(1)
```

## Workflow Integration

NotificationAgent is used in multiple workflows:

### order_placement
1. CartAgent validates cart
2. OrderAgent creates order
3. **NotificationAgent** sends order confirmation

### subscription_management
1. SubscriptionAgent manages subscription
2. **NotificationAgent** sends renewal reminders

## Events

| Event | Trigger | Notification Type |
|-------|---------|-------------------|
| order_placed | create_order_notification() | order |
| order_shipped | create_delivery_notification() | delivery |
| order_delivered | create_delivery_notification() | delivery |
| subscription_created | create_subscription_notification() | subscription |
| subscription_cancelled | create_subscription_notification() | subscription |
| new_product_added | create_product_notification() | product |

## Frontend Integration

Notifications are displayed via:
- Bell icon in navbar
- Dropdown panel showing recent notifications
- Toast popups for new notifications
- Badge count on bell icon

```javascript
// Frontend API calls
GET /api/notifications           // Get all notifications
GET /api/notifications/unread-count  // Get unread count
POST /api/notifications/{id}/read    // Mark as read
POST /api/notifications/read-all    // Mark all as read
DELETE /api/notifications/{id}      // Delete notification
```
